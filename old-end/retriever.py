from typing import Literal

from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from langgraph.types import StreamWriter

from clients.chat_gpt import ChatGPT, MessageGPT
from tools.tool_neo4j import tools_neo4j

from config import openai
from state import RetrieverInput, RetrieverState
from schemas import retrieval_decision_schema, response_evaluation_schema
from prompts import (
    retrieval_decision_instruction,
    initial_retrieval_instruction,
    advanced_retrieval_instruction,
    response_evaluation_instruction,
)

def Retrieval_Decision(state: RetrieverInput) -> RetrieverState:
    llm = ChatGPT(
        model = openai.gpt_mini_model,
        temperature = 1.0,
        max_tokens = 4096,
    )
    llm.add_structured(retrieval_decision_schema)

    message = MessageGPT()
    message.add_system(retrieval_decision_instruction)
    message.add_user(state["user_input"])

    status = llm.chat(message.prompts).status
    message.remove_system()
    print(f"Retrieval Decision Status: {status}")
    
    return {
        "messages": message.prompts,
        "retrieval_status": status,
    }

def Answer_Generation(state: RetrieverState) -> RetrieverState:
    llm = ChatGPT(
        model = openai.gpt_model,
        temperature = 1.0,
        max_tokens = 8192,
    )

    messages = MessageGPT()
    messages.add_user(state["messages"][-1].content)

    response = llm.chat(messages.prompts)
    print(f"Answer Generation Response: {response}")

    return {"messages": [response]}

def Initial_Retrieval(state: RetrieverState, writer: StreamWriter) -> RetrieverState:
    llm = ChatGPT(
        model = openai.gpt_model,
        temperature = 1.0,
        max_tokens = 8192,
    )
    agent = create_agent(
        llm.model,
        tools = tools_neo4j,
    )

    messages = MessageGPT()
    messages.add_system(initial_retrieval_instruction)
    messages.add_user(state["messages"][-1].content)

    response = agent.invoke({"messages": messages.prompts})
    print("--------------------------------")
    print(f"Initial Retrieval Response:")
    for message in response["messages"]:
        print(f"Message: {message.content}")

    return {"messages": [response["messages"][-1]]}


def Advanced_Retrieval(state: RetrieverState, writer: StreamWriter) -> RetrieverState:
    llm = ChatGPT(
        model = openai.gpt_model,
        temperature = 1.0,
        max_tokens = 16384,
    )
    agent = create_agent(
        llm.model,
        tools = tools_neo4j,
    )

    messages = MessageGPT()
    messages.add_system(advanced_retrieval_instruction)
    messages.add_messages(state["messages"])

    response = agent.invoke({"messages": messages.prompts})
    print("--------------------------------")
    print(f"Advanced Retrieval Response:")
    for message in response["messages"]:
        print(f"Message: {message.content}")

    return {"messages": [response["messages"][-1]]}

def Response_Evaluation(state: RetrieverState, writer: StreamWriter) -> RetrieverState:
    llm = ChatGPT(
        model = openai.gpt_model,
        temperature = 1.0,
        max_tokens = 1024,
    )
    llm.add_structured(response_evaluation_schema)

    message = MessageGPT()
    message.add_system(response_evaluation_instruction)
    message.add_user(f"User Input : {state["messages"][0].content}")
    message.add_user(f"AI Response : {state["messages"][-1].content}")

    status = llm.chat(message.prompts).status
    print(f"Response Evaluation Status: {status}")

    return {"evaluation_status": status}

def should_retrieve(state: RetrieverState) -> Literal["Initial_Retrieval", "Answer_Generation"]:
    if state["retrieval_status"]:
        return "Initial_Retrieval"
    else:
        return "Answer_Generation"

def should_retrieve_again(state: RetrieverState) -> Literal["Advanced_Retrieval", END]:
    if state["evaluation_status"]:
        return "Advanced_Retrieval"
    else:
        return END

graph = (
    StateGraph(RetrieverState, input_schema = RetrieverInput)
    .add_node("Retrieval_Decision", Retrieval_Decision)
    .add_node("Answer_Generation", Answer_Generation)
    .add_node("Initial_Retrieval", Initial_Retrieval)
    .add_node("Advanced_Retrieval", Advanced_Retrieval)
    .add_node("Response_Evaluation", Response_Evaluation)
    .add_edge(START, "Retrieval_Decision")
    .add_conditional_edges("Retrieval_Decision", should_retrieve)
    .add_edge("Initial_Retrieval", "Response_Evaluation")
    .add_conditional_edges("Response_Evaluation", should_retrieve_again)
)

retriever_agent = graph.compile(name = "Retriever Agent")