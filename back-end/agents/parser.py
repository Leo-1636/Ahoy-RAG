import asyncio

from langgraph.graph import StateGraph, START, END
from langgraph.types import StreamWriter

from config import MODEL

from clients.vLLM import ChatVLLM
from clients.YOLO import ChatYOLO
from clients.Neo4j import ChatNeo4j
from clients.Embedder import ChatEmbedder

from components.algorithm import ReadingOrderAlgorithm
from components.processor import DocumentProcessor, DatabaseProcessor
from components.progress import ProgressTracker
from components.message import Message, MessageBatch

from settings.state import ParserState
from settings.prompts import (
    document_summary_schema, document_summary_instruction,
    document_extraction_schema, document_extraction_instruction,
    document_hierarchy_schema, document_hierarchy_instruction,
)

async def Document_Init(state: ParserState, writer: StreamWriter) -> ParserState:
    for document in state.documents:
        processor = DocumentProcessor(document)

        writer(f"Initializing document {document.id}")
        print(f"Initializing document {document.id}")
        try:
            processor.build()
            processor.initialize()
            await asyncio.to_thread(processor.convert_images)
        except Exception as e:
            writer(f"Failed to initialize document {document.id} : {e}")
            print(f"Failed to initialize document {document.id} : {e}")
    return ParserState(mode = state.mode, documents = state.documents)

async def Document_Summary(state: ParserState, writer: StreamWriter) -> ParserState:
    client = ChatVLLM(
        model_name = MODEL.reasoning_model,
        temperature = 1.0,
        max_tokens = 1024,
    ).add_structured(schema = document_summary_schema)
    
    for index, document in enumerate(state.documents):
        processor = DocumentProcessor(document)
        tracker = ProgressTracker()

        tracker.update(index + 1, len(state.documents))
        writer(f"Summarizing document {tracker.current}/{tracker.total} : {tracker.progress}")
        print(f"Summarizing document {tracker.current}/{tracker.total} : {tracker.progress}")
        try:
            message = Message()
            message.add_system(document_summary_instruction)
            message.add_image(processor.load_pages(1, 5))

            summary = await client.async_chat(message.prompts)
            processor.add_summary(summary)
        except Exception as e:
            writer(f"Failed to summarize document {tracker.current}/{tracker.total} : {e}")
            print(f"Failed to summarize document {tracker.current}/{tracker.total} : {e}")
            continue
    client.sleep()
    return ParserState(mode = state.mode, documents = state.documents)

async def Document_Filter(state: ParserState, writer: StreamWriter) -> ParserState:
    return ParserState(mode = state.mode, documents = state.documents)

async def Document_Analyze(state: ParserState, writer: StreamWriter) -> ParserState:
    client = ChatYOLO(model = "model.pt", batch_size = 16)

    for index, document in enumerate(state.documents):
        processor = DocumentProcessor(document)
        processor.initialize()
        
        tracker = ProgressTracker()
        document_progress = f"document {index + 1}/{len(state.documents)}"
        for batch_index in range(1, document.page_number + 1, client.batch_size):
            tracker.update(batch_index, document.page_number)
            writer(f"Detecting page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            print(f"Detecting page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                results = await client.detect_batch(processor.load_pages(batch_index, batch_index + client.batch_size))
                processor.add_detection(results)
            except Exception as e:
                writer(f"Failed to detect page {batch_index}/{document.page_number} of {document_progress} : {e}")
                print(f"Failed to detect page {batch_index}/{document.page_number} of {document_progress} : {e}")
                continue

        tracker.reset()
        for page_id, detection in enumerate(processor.detections):
            tracker.update(page_id + 1, document.page_number)
            writer(f"Analyzing page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            print(f"Analyzing page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                algorithm = ReadingOrderAlgorithm(detection, client.classes)
                processor.load_page(page_id + 1)
                processor.add_contents(algorithm.reading_order)
                processor.add_annotation(algorithm.reading_order)
            except Exception as e:
                writer(f"Failed to analyze page {tracker.current}/{tracker.total} of {document_progress} : {e}")
                print(f"Failed to analyze page {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        processor.save_content_list()
        processor.save_annotation_pdf()
    return ParserState(mode = state.mode, documents = state.documents)

async def Document_Extract(state: ParserState, writer: StreamWriter) -> ParserState:
    client = ChatVLLM(
        model_name = MODEL.reasoning_model,
        temperature = 1.0,
        max_tokens = 4096,
        batch_size = 64,
        timeout = 20,
        max_retries = 0,
    ).add_structured(schema = document_extraction_schema)

    for index, document in enumerate(state.documents):
        processor = DocumentProcessor(document)
        processor.load_content_list()

        tracker = ProgressTracker()
        document_progress = f"document {index + 1}/{len(state.documents)}"
        for batch_index in range(0, len(processor.content_list), client.batch_size):
            tracker.update(batch_index + 1, len(processor.content_list))
            writer(f"Extracting content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            print(f"Extracting content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                batch_message = MessageBatch()
                batch_content = processor.content_list[batch_index : batch_index + client.batch_size]
                for content in batch_content:
                    message = Message()
                    message.add_system(document_extraction_instruction)
                    message.add_image(processor.load_image(content))
                    batch_message.add(message)
                batch_responses = await client.async_batch(batch_message.messages)
                for content_index in range(client.batch_size):
                    processor.update_content(batch_index + content_index, batch_responses[content_index])
            
            except Exception as e:
                writer(f"Failed to extract content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                print(f"Failed to extract content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                for retry_index, content in enumerate(batch_content):
                    tracker.update(batch_index + retry_index + 1, len(processor.content_list))
                    writer(f"Retry Extracting content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
                    print(f"Retry Extracting content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
                    try:
                        message = batch_message.messages[retry_index]
                        response = await client.async_chat(message)
                        processor.update_content(batch_index + retry_index, response)
                    except Exception as e:
                        writer(f"Failed to retry extract content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                        print(f"Failed to retry extract content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                        continue
                continue
            processor.save_content_list()
        
    client.sleep()
    return ParserState(mode = state.mode, documents = state.documents)

async def Database_Init(state: ParserState, writer: StreamWriter) -> ParserState:
    for index, document in enumerate(state.documents):
        processor = DatabaseProcessor(document)
        document_progress = f"document {index + 1}/{len(state.documents)}"
        try:
            writer(f"Initializing database of {document_progress}")
            print(f"Initializing database of {document_progress}")
            processor.create_main_node()
            for page_id in range(1, document.page_number + 1):
                processor.create_page_node(page_id)
            processor.link_pages()
        except Exception as e:
            writer(f"Failed to initialize database of {document_progress} : {e}")
            print(f"Failed to initialize database of {document_progress} : {e}")
            continue
        processor.save_pages()
        processor.save_relationships()
    return ParserState(mode = state.mode, documents = state.documents)

async def Relation_Analyze(state: ParserState, writer: StreamWriter) -> ParserState:
    client = ChatVLLM(
        model_name = MODEL.reasoning_model,
        temperature = 1.0,
        max_tokens = 128,
    ).add_structured(schema = document_hierarchy_schema)

    for index, document in enumerate(state.documents):
        processor = DatabaseProcessor(document)
        processor.load_content_list()
        processor.load_relationships()

        tracker = ProgressTracker()
        document_progress = f"document {index + 1} of {len(state.documents)}"
        for content_index, content in enumerate(processor.content_list):
            tracker.update(content_index + 1, len(processor.content_list))
            writer(f"Analyzing relation {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            print(f"Analyzing relation {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                processor.load_content(content)
                message = Message()
                message.add_system(document_hierarchy_instruction)
                message.add_image(processor.page)
                message.add_user(f"Document Title : {document.title}")
                message.add_user(f"Hierarchy List : {processor.hierarchy_list}")
                message.add_user(f"New Content : {processor.content.text}")

                response = await client.async_chat(message.prompts)
                processor.update_hierarchy(response)
                processor.create_content_node()
                processor.link_sequence()
                processor.link_hierarchy()
            except Exception as e:
                writer(f"Failed to analyze relation {tracker.current}/{tracker.total} of {document_progress} : {e}")
                print(f"Failed to analyze relation {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        processor.save_nodes()
        processor.save_relationships()
    client.sleep()
    return ParserState(mode = state.mode, documents = state.documents)

async def Vector_Embedding(state: ParserState, writer: StreamWriter) -> ParserState:
    client = ChatEmbedder(
        model_name = MODEL.embedding_model,
        dimension = 128,
        batch_size = 4,
        device = "cuda",
    )

    for index, document in enumerate(state.documents):
        processor = DatabaseProcessor(document)
        processor.load_page_nodes()
        processor.load_nodes()

        tracker = ProgressTracker()
        document_progress = f"document {index + 1} of {len(state.documents)}"
        for batch_index in range(1, len(processor.page_nodes), client.batch_size):
            tracker.update(batch_index, len(processor.page_nodes) - 1)
            writer(f"Embedding page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            print(f"Embedding page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                batch_image = processor.load_pages(batch_index, batch_index + client.batch_size)
                batch_vector = await asyncio.to_thread(client.encode_image, batch_image)
                for page_index, vector in enumerate(batch_vector):
                    page_id = batch_index + page_index
                    processor.embed_page(page_id, vector)
            except Exception as e:
                writer(f"Failed to embed page {tracker.current}/{tracker.total} of {document_progress} : {e}")
                print(f"Failed to embed page {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        
        tracker.reset()
        for batch_index in range(0, len(processor.nodes), client.batch_size):
            tracker.update(batch_index + 1, len(processor.nodes))
            writer(f"Embedding content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            print(f"Embedding content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                batch_text = processor.load_text(batch_index, client.batch_size)
                batch_image = processor.load_image(batch_index, client.batch_size)
                batch_text_vector = await asyncio.to_thread(client.encode_text, batch_text)
                batch_image_vector = await asyncio.to_thread(client.encode_image, batch_image)
                for content_index, text_vector, image_vector in zip(range(batch_text_vector), batch_text_vector, batch_image_vector):
                    content_id = batch_index + content_index
                    processor.embed_content(content_id, text_vector, image_vector)
            except Exception as e:
                writer(f"Failed to embed content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                print(f"Failed to embed content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        processor.save_nodes()
    client.close()
    return ParserState(mode = state.mode, documents = state.documents)

async def Database_Storage(state: ParserState, writer: StreamWriter) -> ParserState:
    database = ChatNeo4j()
    for document in state.documents:
        processor = DatabaseProcessor(document)
        processor.load_page_nodes()
        processor.load_nodes()
        processor.load_relationships()

        writer(f"Storing database of {document.id}")
        print(f"Storing database of {document.id}")
        try:
            await database.write_graph(
                nodes = processor.page_nodes + processor.nodes,
                relationships = processor.relationships,
            )
        except Exception as e:
            writer(f"Failed to store database of {document.id} : {e}")
            print(f"Failed to store database of {document.id} : {e}")
            continue
    await database.close()
    return ParserState(mode = state.mode, documents = state.documents)

def Parser_Route(state: ParserState):
    return state.mode

workflow = (
    StateGraph(ParserState)
    .add_node("Document_Init", Document_Init)
    .add_node("Document_Summary", Document_Summary)
    .add_node("Document_Filter", Document_Filter)
    .add_node("Document_Analyze", Document_Analyze)
    .add_node("Document_Extract", Document_Extract)
    .add_node("Database_Init", Database_Init)
    .add_node("Relation_Analyze", Relation_Analyze)
    .add_node("Vector_Embedding", Vector_Embedding)
    .add_node("Database_Storage", Database_Storage)

    .add_conditional_edges(START, Parser_Route, 
        {
            "Fast Parse": "Document_Init",
            "Deep Parse": "Document_Init",
            "Fast to Deep Parse": "Document_Analyze",
        }
    )
    .add_edge("Document_Init", "Document_Summary")
    .add_edge("Document_Summary", "Document_Filter")
    .add_conditional_edges("Document_Filter", Parser_Route,
        {
            "Fast Parse": "Database_Init",
            "Deep Parse": "Document_Analyze",
            "Fast to Deep Parse": "Document_Analyze",
        }
    )
    .add_edge("Document_Analyze", "Document_Extract")
    .add_edge("Document_Extract", "Database_Init")
    .add_edge("Database_Init", "Relation_Analyze")
    .add_edge("Relation_Analyze", "Vector_Embedding")
    .add_edge("Vector_Embedding", "Database_Storage")
    .add_edge("Database_Storage", END)
)

parser_agent = workflow.compile()