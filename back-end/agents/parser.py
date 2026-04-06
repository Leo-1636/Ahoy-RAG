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

<<<<<<< HEAD
async def Document_Init(state: ParserState, streamer: StreamWriter) -> ParserState:
    for document in state.documents:
        processor = DocumentProcessor(document)

        streamer(f"Initializing document {document.id}")
=======
async def Document_Init(state: ParserInput, writer: StreamWriter) -> ParserState:
    documents = []
    tracker = Tracker()
    for index, document_id in enumerate(state.document_ids):
        progress = tracker.get_progress(index + 1, len(state.document_ids))
        print(f"Initializing document {tracker.index} of {tracker.total} : {progress}")
        writer(f"Initializing document {tracker.index} of {tracker.total} : {progress}")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
        try:
            processor.initialize()
            await asyncio.to_thread(processor.convert_images)
        except Exception as e:
<<<<<<< HEAD
            streamer(f"Failed to initialize document {document.id} : {e}")
    return ParserState(mode = state.mode, documents = state.documents)
=======
            print(f"Failed to initialize document {tracker.index} of {tracker.total} : {e}")
            writer(f"Failed to initialize document {tracker.index} of {tracker.total} : {e}")
            continue
        await asyncio.sleep(0.1)
    return ParserState(documents = documents)
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd

async def Document_Summary(state: ParserState, streamer: StreamWriter) -> ParserState:
    client = ChatVLLM(
        model_name = MODEL.reasoning_model,
        temperature = 1.0,
        max_tokens = 1024,
<<<<<<< HEAD
    ).add_structured(schema = document_summary_schema)
    
    for index, document in enumerate(state.documents):
        processor = DocumentProcessor(document)
        tracker = ProgressTracker()

        tracker.update(index + 1, len(state.documents))
        streamer(f"Summarizing document {tracker.current}/{tracker.total} : {tracker.progress}")
        try:
            message = Message()
            message.add_system(document_summary_instruction)
            message.add_image(processor.load_pages(1, 6))

            summary = await client.async_chat(message.prompts)
            processor.add_summary(summary)
        except Exception as e:
            streamer(f"Failed to summarize document {tracker.current}/{tracker.total} : {e}")
=======
    ).add_structured(document_summary_schema)

    documents = []
    tracker = Tracker()
    for index, document in enumerate(state.documents):
        progress = tracker.get_progress(index + 1, len(state.documents))
        print(f"Summarizing document {tracker.index} of {tracker.total} : {progress}")
        writer(f"Summarizing document {tracker.index} of {tracker.total} : {progress}")
        try:
            summarizer = Summarizer(document)
            messages = (
                Message()
                .add_system(document_summary_instruction)
                .add_image(summarizer.pages)
            )
            summary = await llm.chat(messages.prompts)
            summarizer.load_metadata(summary)
            summarizer.update_metadata(documents)
        except Exception as e:
            print(f"Failed to summarize document {tracker.index} of {tracker.total} : {e}")
            writer(f"Failed to summarize document {tracker.index} of {tracker.total} : {e}")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
            continue
    client.sleep()
    return ParserState(mode = state.mode, documents = state.documents)

<<<<<<< HEAD
async def Document_Filter(state: ParserState, streamer: StreamWriter) -> ParserState:
    return ParserState(mode = state.mode, documents = state.documents)

async def Document_Analyze(state: ParserState, streamer: StreamWriter) -> ParserState:
    client = ChatYOLO(model = "model.pt", batch_size = 16)
=======
async def Document_Analyze(state: ParserState, writer: StreamWriter) -> ParserState:
    yolo = ChatYOLO(model = "DLA.pt")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd

    for index, document in enumerate(state.documents):
<<<<<<< HEAD
        processor = DocumentProcessor(document)

        tracker = ProgressTracker()
        document_progress = f"document {index + 1}/{len(state.documents)}"
        for batch_index in range(1, document.page_number + 1, client.batch_size):
            tracker.update(batch_index, document.page_number)
            streamer(f"Detecting page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                results = await client.detect_batch(processor.load_pages(batch_index, batch_index + client.batch_size))
                processor.add_detection(results)
            except Exception as e:
                streamer(f"Failed to detect page {batch_index}/{document.page_number} of {document_progress} : {e}")
                continue

        tracker.reset()
        for page_id, detection in enumerate(processor.detections):
            tracker.update(page_id, document.page_number)
            streamer(f"Analyzing page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                algorithm = ReadingOrderAlgorithm(detection, client.classes)
                processor.load_page(page_id)
                processor.add_contents(algorithm.reading_order)
                processor.add_annotation(algorithm.reading_order)
            except Exception as e:
                streamer(f"Failed to analyze page {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        processor.save_content_list()
        processor.save_annotation_pdf()
    return ParserState(mode = state.mode, documents = state.documents)

async def Document_Extract(state: ParserState, streamer: StreamWriter) -> ParserState:
    client = ChatVLLM(
        model_name = MODEL.reasoning_model,
        temperature = 1.0,
        max_tokens = 4096,
        batch_size = 64,
        timeout = 20,
        max_retries = 0,
    ).add_structured(schema = document_extraction_schema)
=======
        persister = Persister(document)
        for page_id in range(1, persister.page_number + 1):
            progress = tracker.get_progress(page_id, persister.page_number)
            print(f"Analyzing page {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            writer(f"Analyzing page {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            try:
                yolo.detect(persister.load_page(page_id))
                analyzer = LayoutAnalyzer(yolo.detections, yolo.class_names)
                persister.add_content_list(analyzer.sort_elements())
                persister.add_annotation_pdf()
            except Exception as e:
                print(f"Failed to analyze page {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                writer(f"Failed to analyze page {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                continue
            await asyncio.sleep(0.1)
        persister.save_content_list()
        persister.save_annotation_pdf()
    return ParserState(documents = state.documents)

async def Document_Extract(state: ParserState, writer: StreamWriter) -> ParserState:
    llm = ChatVLLM(
        model = model.reasoning_model,
        temperature = 0.0,
        max_tokens = 8192, 
        batch_size = 32,
        timeout = 20,
    ).add_structured(document_extraction_schema)
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd

    for index, document in enumerate(state.documents):
<<<<<<< HEAD
        processor = DocumentProcessor(document)
        processor.load_content_list()

        tracker = ProgressTracker()
        document_progress = f"document {index + 1}/{len(state.documents)}"
        for batch_index in range(0, len(processor.content_list), client.batch_size):
            tracker.update(batch_index + 1, len(processor.content_list))
            streamer(f"Extracting content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
=======
        persister = Persister(document).load_content_list()
        for batch_index in range(0, len(persister.content_list), llm.batch_size):
            progress = tracker.get_progress(batch_index + 1, len(persister.content_list))
            print(f"Extracting content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            writer(f"Extracting content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
            try:
                batch_message = MessageBatch()
                batch_content = processor.content_list[batch_index : batch_index + client.batch_size]
                for content in batch_content:
<<<<<<< HEAD
                    message = Message()
                    message.add_system(document_extraction_instruction)
                    message.add_image(processor.load_image(content))
                    batch_message.add(message)
                batch_responses = await client.async_batch(batch_message.messages)
                for content_index in range(client.batch_size):
                    processor.update_content(batch_index + content_index, batch_responses[content_index])
            
            except Exception as e:
                streamer(f"Failed to extract content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                for retry_index, content in enumerate(batch_content):
                    tracker.update(batch_index + retry_index + 1, len(processor.content_list))
                    streamer(f"Retry Extracting content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
                    try:
                        message = batch_message.messages[retry_index]
                        response = await client.async_chat(message)
                        processor.update_content(batch_index + retry_index, response)
                    except Exception as e:
                        streamer(f"Failed to retry extract content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                        continue
                continue
            processor.save_content_list()
        
    client.sleep()
    return ParserState(mode = state.mode, documents = state.documents)

async def Database_Init(state: ParserState, streamer: StreamWriter) -> ParserState:
    for index, document in enumerate(state.documents):
        processor = DatabaseProcessor(document)
        document_progress = f"document {index + 1}/{len(state.documents)}"
        try:
            streamer(f"Initializing database of {document_progress}")
            processor.create_main_node()
            for page_id in range(1, document.page_number + 1):
                processor.create_page_node(page_id)
            processor.link_pages()
        except Exception as e:
            streamer(f"Failed to initialize database of {document_progress} : {e}")
            continue
        processor.save_pages()
        processor.save_relationships()
    return ParserState(mode = state.mode, documents = state.documents)
=======
                    message = (
                        Message()
                        .add_system(document_extraction_instruction)
                        .add_image(persister.load_image(content))
                    )
                    batch_prompts.add_prompts(message.prompts)
                batch_responses = await llm.chat_batch(batch_prompts.messages)
                persister.update_contents(batch_content, batch_responses)
            except Exception as e:
                print(f"Failed to extract content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                writer(f"Failed to extract content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                
                for retry_index, content in enumerate(batch_content):
                    try:
                        progress = tracker.get_progress(batch_index + retry_index + 1, len(persister.content_list))
                        print(f"Retry Extracting content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
                        writer(f"Retry Extracting content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
                        message = (
                            Message()
                            .add_system(document_extraction_instruction)
                            .add_image(persister.load_image(content))
                        )
                        response = await llm.chat(message.prompts)
                        persister.update_content(content, response)
                    except Exception as e:
                        print(f"Failed to retry extract content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                        writer(f"Failed to retry extract content {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                        continue
                continue
            await asyncio.sleep(0.1)
        llm.sleep()
        persister.save_content_list()
    return ParserState(documents = state.documents)

async def Relation_Analyze(state: ParserState, writer: StreamWriter) -> ParserState:
    llm = ChatVLLM(
        model = model.reasoning_model,
        temperature = 0.0,
        max_tokens = 32,
    ).add_structured(document_hierarchy_schema)

    tracker = Tracker()
    for index, document in enumerate(state.documents):
        analyzer = GraphAnalyzer(document)
        persister = Persister(document).load_content_list()
        
        analyzer.add_document_node()
        for page_id in range(1, persister.page_number + 1):
            analyzer.add_page_node(page_id)

        for content_index, content in enumerate(persister.content_list):
            progress = tracker.get_progress(content_index + 1, len(persister.content_list))
            print(f"Analyzing relation {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            writer(f"Analyzing relation {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            try:
                persister.load_content(content)
                messages = (
                    Message()
                    .add_system(document_hierarchy_instruction)
                    .add_image(persister.load_page(persister.page_id))
                    .add_user(f"Document Title : {persister.title}")
                    .add_user(f"Hierarchy List : {analyzer.hierarchy_list}")
                    .add_user(f"New Content : {persister.content_text}")
                )
                analyzer.update_hierarchy(await llm.chat(messages.prompts), persister.content_text)
                analyzer.add_content_node(content)
                analyzer.add_sequence_relationship()
                analyzer.add_hierarchy_relationship()
            except Exception as e:
                print(f"Failed to analyze relation {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                writer(f"Failed to analyze relation {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                continue
            await asyncio.sleep(0.1)
        persister.save_graph_data(analyzer.load_nodes(), analyzer.relationships)
    llm.sleep()
    return ParserState(documents = state.documents)
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd

async def Relation_Analyze(state: ParserState, streamer: StreamWriter) -> ParserState:
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
            streamer(f"Analyzing relation {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
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
                streamer(f"Failed to analyze relation {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        processor.save_nodes()
        processor.save_relationships()
    client.sleep()
    return ParserState(mode = state.mode, documents = state.documents)

async def Vector_Embedding(state: ParserState, streamer: StreamWriter) -> ParserState:
    client = ChatEmbedder(
        model_name = MODEL.embedding_model,
        dimension = 128,
        batch_size = 4,
        device = "cuda",
    )

    for index, document in enumerate(state.documents):
<<<<<<< HEAD
        processor = DatabaseProcessor(document)
        processor.load_page_nodes()
        processor.load_nodes()
=======
        embedder = DatabaseEmbedder(document)

        for page_id in range(1, embedder.page_number + 1, llm.batch_size):
            progress = tracker.get_progress(page_id, len(embedder.nodes))
            print(f"Embedding page node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            writer(f"Embedding page node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            try:
                batch_page = embedder.load_batch_page(page_id, llm.batch_size)
                batch_page_vector = llm.encode_image(batch_page)
                embedder.embed_page(batch_page_vector)
            except Exception as e:
                print(f"Failed to embed page node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                writer(f"Failed to embed page node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                continue
            await asyncio.sleep(0.1)

        for batch_index in range(embedder.page_number + 1, len(embedder.nodes), llm.batch_size):
            progress = tracker.get_progress(batch_index + 1, len(embedder.nodes))
            print(f"Embedding content node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            writer(f"Embedding content node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {progress}")
            try:
                batch_text, batch_image = embedder.load_batch_content(batch_index, llm.batch_size)
                batch_text_vector = llm.encode_text(batch_text)
                batch_image_vector = llm.encode_image(batch_image)
                embedder.embed_content(batch_text_vector, batch_image_vector)
            except Exception as e:
                print(f"Failed to embed content node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                writer(f"Failed to embed content node {tracker.index} of {tracker.total} of document {index + 1} of {len(state.documents)} : {e}")
                continue
            await asyncio.sleep(0.1)
        embedder.update_nodes()
    llm.close()
    return ParserState(documents = state.documents)
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd

        tracker = ProgressTracker()
        document_progress = f"document {index + 1} of {len(state.documents)}"
        for batch_index in range(1, len(processor.page_nodes), client.batch_size):
            tracker.update(batch_index, len(processor.page_nodes) - 1)
            streamer(f"Embedding page {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                batch_image = processor.load_pages(batch_index, batch_index + client.batch_size)
                batch_vector = await asyncio.to_thread(client.encode_image, batch_image)
                for page_index in range(client.batch_size):
                    page_id = batch_index + page_index
                    processor.embed_page(page_id, batch_vector[page_index])
            except Exception as e:
                streamer(f"Failed to embed page {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        
        tracker.reset()
        for batch_index in range(0, len(processor.nodes), client.batch_size):
            tracker.update(batch_index + 1, len(processor.nodes))
            streamer(f"Embedding content {tracker.current}/{tracker.total} of {document_progress} : {tracker.progress}")
            try:
                batch_text = processor.load_text(batch_index, client.batch_size)
                batch_image = processor.load_image(batch_index, client.batch_size)
                batch_text_vector = await asyncio.to_thread(client.encode_text, batch_text)
                batch_image_vector = await asyncio.to_thread(client.encode_image, batch_image)
                for content_index in range(client.batch_size):
                    content_id = batch_index + content_index
                    processor.embed_content(content_id, batch_text_vector[content_index], batch_image_vector[content_index])
            except Exception as e:
                streamer(f"Failed to embed content {tracker.current}/{tracker.total} of {document_progress} : {e}")
                continue
        processor.save_nodes()
    client.close()
    return ParserState(mode = state.mode, documents = state.documents)

async def Database_Storage(state: ParserState, streamer: StreamWriter) -> ParserState:
    database = ChatNeo4j()
<<<<<<< HEAD
    for document in state.documents:
        processor = DatabaseProcessor(document)
        processor.load_page_nodes()
        processor.load_nodes()
        processor.load_relationships()

        streamer(f"Storing database of {document.id}...")
        try:
            await database.write_graph(
                nodes = processor.page_nodes + processor.nodes,
                relationships = processor.relationships,
=======
    tracker = Tracker()
    for index, document in enumerate(state.documents):
        embedder = DatabaseEmbedder(document)
        progress = tracker.get_progress(index + 1, len(state.documents))
        print(f"Storing database document {index + 1} of {len(state.documents)} : {progress}")
        writer(f"Storing database document {index + 1} of {len(state.documents)} : {progress}")
        try:
            await database.write_graph(
                nodes = embedder.nodes,
                relationships = embedder.relationships,
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
            )
            await database.create_index()
        except Exception as e:
<<<<<<< HEAD
            streamer(f"Failed to store database of {document.id} : {e}")
=======
            print(f"Failed to store database document {index + 1} of {len(state.documents)} : {e}")
            writer(f"Failed to store database document {index + 1} of {len(state.documents)} : {e}")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
            continue
    database.close()
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
    .add_edge("Database_Init", "Relation_Analyze")
    .add_edge("Relation_Analyze", "Vector_Embedding")
    .add_edge("Vector_Embedding", "Database_Storage")
    .add_edge("Database_Storage", END)
)

<<<<<<< HEAD
parser_agent = workflow.compile()
=======
parser_agent = workflow.compile(name = "Parser Agent")
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
