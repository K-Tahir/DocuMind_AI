# # core/rag_engine.py
# Version: 1

# import os
# import re
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from langchain_community.vectorstores import Chroma
# try:
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
# except ImportError:
#     from langchain.text_splitter import RecursiveCharacterTextSplitter
# try:
#     from langchain_core.documents import Document
# except ImportError:
#     from langchain.docstore.document import Document
# from langchain_core.prompts import ChatPromptTemplate
# from config import CHROMA_DIR
# from core.parser import parse_file

# def clean_collection_name(session_id: str) -> str:
#     """Cleans the session ID into a valid Chroma collection name."""
#     cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
#     if not cleaned[0].isalnum():
#         cleaned = "col_" + cleaned
#     cleaned = cleaned[:63]
#     return cleaned

# def process_and_index_doc(file_path: str, session_id: str, api_key: str):
#     """Chunks the parsed document pages and indexes them in a session-specific vector collection."""
#     print(f"[INFO] Indexing document for session {session_id}: {file_path}")
    
#     # 1. Parse the file into text and pages
#     parsed = parse_file(file_path)
#     doc_name = os.path.basename(file_path)
    
#     documents = []
#     if parsed.get("pages"):
#         for p in parsed["pages"]:
#             documents.append(Document(
#                 page_content=p["text"],
#                 metadata={"page": p["page"], "source": doc_name}
#             ))
#     else:
#         # If document has no individual pages (TXT, CSV, XLSX, etc.)
#         documents.append(Document(
#             page_content=parsed.get("text", ""),
#             metadata={"page": 1, "source": doc_name}
#         ))
        
#     # 2. Chunk the documents
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     final_chunks = text_splitter.split_documents(documents)
    
#     # Set the key into the environment variables
#     os.environ["GOOGLE_API_KEY"] = api_key
    
#     # 3. Embed and store in Chroma
#     embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
#     collection_name = clean_collection_name(session_id)
    
#     # If the collection already exists, Chroma will add new documents or we can recreate it
#     # We will overwrite/re-index for a fresh session
#     try:
#         # Check if collection exists and delete it first for clean indexing
#         db_check = Chroma(
#             persist_directory=CHROMA_DIR,
#             embedding_function=embeddings,
#             collection_name=collection_name
#         )
#         # Delete if documents exist
#         if db_check.get()["ids"]:
#             db_check.delete_collection()
#             print(f"[INFO] Deleted existing collection: {collection_name}")
#     except Exception as e:
#         print(f"[INFO] Creating new collection: {collection_name} (details: {e})")
        
#     vector_store = Chroma.from_documents(
#         documents=final_chunks, 
#         embedding=embeddings, 
#         persist_directory=CHROMA_DIR,
#         collection_name=collection_name
#     )
#     print(f"[SUCCESS] Vector store populated with {len(final_chunks)} chunks in collection: {collection_name}")
#     return vector_store.as_retriever(search_kwargs={"k": 4})

# def query_document(session_id: str, query: str, api_key: str) -> str:
#     """Retrieves session-specific context and queries Gemini, enforcing page citations."""
#     os.environ["GOOGLE_API_KEY"] = api_key
#     embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
#     collection_name = clean_collection_name(session_id)
    
#     # Load collection
#     vector_store = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings,
#         collection_name=collection_name
#     )
    
#     # Retrieve documents
#     retriever = vector_store.as_retriever(search_kwargs={"k": 4})
#     docs = retriever.invoke(query)
    
#     if not docs:
#         return "No relevant context found in the document. Please verify the document has text content."
        
#     # Format context with explicit source and page indicators
#     formatted_context_list = []
#     for d in docs:
#         page = d.metadata.get("page", "N/A")
#         source = d.metadata.get("source", "Document")
#         formatted_context_list.append(f"--- Source: {source}, Page: {page} ---\n{d.page_content}")
#     context = "\n\n".join(formatted_context_list)
    
#     # Define system instructions for page numbering Q&A
#     system_prompt = (
#         "You are an expert document analysis assistant.\n"
#         "Answer the user's question using the provided context below. "
#         "Each block of context begins with a page reference like '--- Source: <filename>, Page: <page_num> ---'.\n"
#         "In your response, you MUST cite the specific page numbers (e.g., '[Page 258]') where you found the information. "
#         "If you cannot find the answer in the context, say that you don't know or that the context does not contain the answer.\n\n"
#         "Context:\n{context}"
#     )
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ])
    
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         google_api_key=api_key,
#         temperature=0.3,
#         convert_system_message_to_human=True
#     )
    
#     formatted_prompt = prompt.format(context=context, input=query)
    
#     # Generate answer
#     response = llm.invoke(formatted_prompt)
#     return response.content

# Version 2
# core/rag_engine.py
# import os
# import re
# from langchain_community.vectorstores import Chroma

# try:
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
# except ImportError:
#     from langchain.text_splitter import RecursiveCharacterTextSplitter

# try:
#     from langchain_core.documents import Document
# except ImportError:
#     from langchain.docstore.document import Document

# from langchain_core.prompts import ChatPromptTemplate
# from config import CHROMA_DIR
# from core.parser import parse_file


# # ── Provider Factory Helpers ───────────────────────────────────────────────

# def _get_embeddings(provider: str, api_key: str, ollama_base_url: str = "http://localhost:11434"):
#     """
#     Returns the correct LangChain embedding object for the active provider.
#     Raises a clear ValueError if a required key is missing.
#     """
#     provider = provider.strip()

#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError("Gemini API key is not set. Go to Settings → Gemini API Key.")
#         from langchain_google_genai import GoogleGenerativeAIEmbeddings
#         # Pass key explicitly — never rely solely on env var
#         return GoogleGenerativeAIEmbeddings(
#             model="models/embedding-001",
#             google_api_key=api_key
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError("OpenAI API key is not set. Go to Settings → OpenAI API Key.")
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=api_key
#         )

#     elif provider == "Claude":
#         # Anthropic has no native embedding model.
#         # We fall back to OpenAI embeddings using the OpenAI key.
#         if not api_key:
#             raise ValueError(
#                 "Claude selected — embeddings use OpenAI.\n"
#                 "Please also set your OpenAI API key in Settings."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=api_key
#         )

#     elif provider == "Ollama":
#         from langchain_community.embeddings import OllamaEmbeddings
#         return OllamaEmbeddings(
#             model="nomic-embed-text",
#             base_url=ollama_base_url
#         )

#     else:
#         raise ValueError(f"Unsupported provider: '{provider}'. Choose from Gemini, OpenAI, Claude, Ollama.")


# def _get_llm(provider: str, api_key: str, model: str,
#              ollama_base_url: str = "http://localhost:11434"):
#     """
#     Returns the correct LangChain chat LLM for the active provider.
#     """
#     provider = provider.strip()

#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError("Gemini API key is not set. Go to Settings → Gemini API Key.")
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         return ChatGoogleGenerativeAI(
#             model=model or "gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0.3,
#             convert_system_message_to_human=True
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError("OpenAI API key is not set. Go to Settings → OpenAI API Key.")
#         from langchain_openai import ChatOpenAI
#         return ChatOpenAI(
#             model=model or "gpt-4o",
#             openai_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Claude":
#         if not api_key:
#             raise ValueError("Claude API key is not set. Go to Settings → Claude API Key.")
#         from langchain_anthropic import ChatAnthropic
#         return ChatAnthropic(
#             model=model or "claude-sonnet-4-6",
#             anthropic_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Ollama":
#         from langchain_community.chat_models import ChatOllama
#         return ChatOllama(
#             model=model or "llama3",
#             base_url=ollama_base_url,
#             temperature=0.3
#         )

#     else:
#         raise ValueError(f"Unsupported provider: '{provider}'.")


# # ── Collection Name Sanitizer ──────────────────────────────────────────────

# def clean_collection_name(session_id: str) -> str:
#     """Sanitizes session ID into a valid ChromaDB collection name."""
#     cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
#     if not cleaned[0].isalnum():
#         cleaned = "col_" + cleaned
#     return cleaned[:63]


# # ── Core RAG Functions ─────────────────────────────────────────────────────

# def process_and_index_doc(file_path: str, session_id: str, api_key: str):
#     """
#     Parses the document, chunks it, embeds it with the active provider,
#     and stores chunks in a session-specific ChromaDB collection.
#     """
#     import config

#     provider       = config.ACTIVE_PROVIDER
#     ollama_url     = config.OLLAMA_BASE_URL

#     # For Claude, embeddings use the OpenAI key
#     embedding_key  = api_key
#     if provider == "Claude":
#         embedding_key = config.OPENAI_API_KEY
#         if not embedding_key:
#             raise ValueError(
#                 "Claude uses OpenAI for embeddings.\n"
#                 "Please set your OpenAI API key in Settings as well."
#             )

#     print(f"[INFO] Indexing '{file_path}' | Provider: {provider} | Session: {session_id}")

#     # 1. Parse
#     parsed   = parse_file(file_path)
#     doc_name = os.path.basename(file_path)

#     documents = []
#     if parsed.get("pages"):
#         for p in parsed["pages"]:
#             documents.append(Document(
#                 page_content=p["text"],
#                 metadata={"page": p["page"], "source": doc_name}
#             ))
#     else:
#         documents.append(Document(
#             page_content=parsed.get("text", ""),
#             metadata={"page": 1, "source": doc_name}
#         ))

#     # 2. Chunk
#     splitter    = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     final_chunks = splitter.split_documents(documents)

#     # 3. Build embedding model
#     embeddings = _get_embeddings(provider, embedding_key, ollama_url)

#     # 4. Wipe existing collection and re-index
#     collection_name = clean_collection_name(session_id)
#     try:
#         db_check = Chroma(
#             persist_directory=CHROMA_DIR,
#             embedding_function=embeddings,
#             collection_name=collection_name
#         )
#         if db_check.get()["ids"]:
#             db_check.delete_collection()
#             print(f"[INFO] Cleared existing collection: {collection_name}")
#     except Exception as e:
#         print(f"[INFO] Fresh collection will be created: {e}")

#     vector_store = Chroma.from_documents(
#         documents=final_chunks,
#         embedding=embeddings,
#         persist_directory=CHROMA_DIR,
#         collection_name=collection_name
#     )

#     print(f"[SUCCESS] Indexed {len(final_chunks)} chunks → collection '{collection_name}' [{provider}]")
#     return vector_store.as_retriever(search_kwargs={"k": 4})


# def query_document(session_id: str, query: str, api_key: str) -> str:
#     """
#     Retrieves relevant chunks from ChromaDB and queries the active LLM provider
#     with enforced page-level citations in the response.
#     """
#     import config

#     provider   = config.ACTIVE_PROVIDER
#     ollama_url = config.OLLAMA_BASE_URL
#     model      = config.get_active_chat_model()

#     # For Claude, embeddings use OpenAI key
#     embedding_key = api_key
#     if provider == "Claude":
#         embedding_key = config.OPENAI_API_KEY
#         if not embedding_key:
#             raise ValueError(
#                 "Claude uses OpenAI for embeddings.\n"
#                 "Please set your OpenAI API key in Settings."
#             )

#     print(f"[INFO] Querying session '{session_id}' | Provider: {provider} | Model: {model}")

#     # 1. Load vector store
#     embeddings  = _get_embeddings(provider, embedding_key, ollama_url)
#     collection_name = clean_collection_name(session_id)

#     vector_store = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings,
#         collection_name=collection_name
#     )

#     # 2. Retrieve relevant chunks
#     retriever = vector_store.as_retriever(search_kwargs={"k": 4})
#     docs      = retriever.invoke(query)

#     if not docs:
#         return (
#             "No relevant content found for your query.\n"
#             "Please verify the document was indexed successfully."
#         )

#     # 3. Format context with page references
#     context_blocks = []
#     for d in docs:
#         page   = d.metadata.get("page", "N/A")
#         source = d.metadata.get("source", "Document")
#         context_blocks.append(
#             f"--- Source: {source}, Page: {page} ---\n{d.page_content}"
#         )
#     context = "\n\n".join(context_blocks)

#     # 4. Build prompt
#     system_prompt = (
#         "You are an expert document analysis assistant.\n"
#         "Answer the user's question using ONLY the provided context below.\n"
#         "Each context block starts with '--- Source: <file>, Page: <num> ---'.\n"
#         "You MUST cite specific page numbers in your answer (e.g. [Page 3]).\n"
#         "If the context does not contain the answer, say so clearly.\n\n"
#         "Context:\n{context}"
#     )

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ])

#     # 5. Get LLM and generate answer
#     llm            = _get_llm(provider, api_key, model, ollama_url)
#     formatted      = prompt.format(context=context, input=query)
#     response       = llm.invoke(formatted)

#     return response.content


# Version 3

# # core/rag_engine.py
# import os
# import re

# from langchain_community.vectorstores import Chroma

# try:
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
# except ImportError:
#     from langchain.text_splitter import RecursiveCharacterTextSplitter

# try:
#     from langchain_core.documents import Document
# except ImportError:
#     from langchain.docstore.document import Document

# from langchain_core.prompts import ChatPromptTemplate
# from config import CHROMA_DIR
# from core.parser import parse_file


# # ── Provider Factory — Embeddings ──────────────────────────────────────────

# def _get_embeddings(provider: str, api_key: str,
#                     ollama_base_url: str = "http://localhost:11434"):
#     """
#     Returns the correct LangChain embedding object.
#     Key is also guaranteed to be in os.environ before this is called
#     (config._inject_env_vars handles that), but we pass it explicitly
#     as well so there is zero ambiguity.
#     """
#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open Settings → paste your key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import GoogleGenerativeAIEmbeddings
#         return GoogleGenerativeAIEmbeddings(
#             model="models/embedding-001",
#             google_api_key=api_key
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=api_key
#         )

#     elif provider == "Claude":
#         # Anthropic has no embedding model — we use OpenAI embeddings
#         import config as _cfg
#         openai_key = _cfg.OPENAI_API_KEY
#         if not openai_key:
#             raise ValueError(
#                 "Claude was selected as provider.\n"
#                 "Claude has no embedding model so DocuMind uses OpenAI for indexing.\n"
#                 "Please also set your OpenAI API key in Settings."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=openai_key
#         )

#     elif provider == "Ollama":
#         from langchain_community.embeddings import OllamaEmbeddings
#         return OllamaEmbeddings(
#             model="nomic-embed-text",
#             base_url=ollama_base_url
#         )

#     else:
#         raise ValueError(
#             f"Unknown provider: '{provider}'.\n"
#             "Supported: Gemini, OpenAI, Claude, Ollama."
#         )


# # ── Provider Factory — Chat LLM ────────────────────────────────────────────

# def _get_llm(provider: str, api_key: str, model: str,
#              ollama_base_url: str = "http://localhost:11434"):
#     """Returns the correct LangChain chat LLM for the active provider."""

#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open Settings → paste your key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         return ChatGoogleGenerativeAI(
#             model=model or "gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0.3,
#             convert_system_message_to_human=True
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import ChatOpenAI
#         return ChatOpenAI(
#             model=model or "gpt-4o",
#             openai_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Claude":
#         if not api_key:
#             raise ValueError(
#                 "Claude API key is not set.\n"
#                 "Open Settings → paste your Anthropic key → click ⚡ Apply Now."
#             )
#         from langchain_anthropic import ChatAnthropic
#         return ChatAnthropic(
#             model=model or "claude-sonnet-4-6",
#             anthropic_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Ollama":
#         from langchain_community.chat_models import ChatOllama
#         return ChatOllama(
#             model=model or "llama3",
#             base_url=ollama_base_url,
#             temperature=0.3
#         )

#     else:
#         raise ValueError(f"Unknown provider: '{provider}'.")


# # ── Collection Name Sanitizer ──────────────────────────────────────────────

# def clean_collection_name(session_id: str) -> str:
#     cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
#     if not cleaned[0].isalnum():
#         cleaned = "col_" + cleaned
#     return cleaned[:63]


# # ── Core: Index Document ───────────────────────────────────────────────────

# def process_and_index_doc(file_path: str, session_id: str, api_key: str = None):
#     """
#     Parses the document, chunks it, embeds with the active provider,
#     and stores in a session-specific ChromaDB collection.

#     NOTE: api_key parameter is kept for backward-compat but IGNORED.
#     Keys are always read fresh from config at call time so stale
#     lambda captures can never cause 'key not set' errors.
#     """
#     # ── Always read live values from config — never trust the passed-in key ──
#     import config
#     provider       = config.ACTIVE_PROVIDER
#     live_api_key   = config.get_active_api_key()
#     ollama_url     = config.OLLAMA_BASE_URL

#     print(f"[INFO] Indexing | Provider: {provider} | Session: {session_id} | File: {file_path}")
#     print(f"[INFO] API Key status: {'✓ present' if live_api_key else '✗ EMPTY'}")

#     # 1. Parse
#     parsed   = parse_file(file_path)
#     doc_name = os.path.basename(file_path)

#     documents = []
#     if parsed.get("pages"):
#         for p in parsed["pages"]:
#             documents.append(Document(
#                 page_content=p["text"],
#                 metadata={"page": p["page"], "source": doc_name}
#             ))
#     else:
#         documents.append(Document(
#             page_content=parsed.get("text", ""),
#             metadata={"page": 1, "source": doc_name}
#         ))

#     # 2. Chunk
#     splitter     = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     final_chunks = splitter.split_documents(documents)

#     # 3. Build embedding model using live key
#     embeddings = _get_embeddings(provider, live_api_key, ollama_url)

#     # 4. Wipe existing collection and re-index fresh
#     collection_name = clean_collection_name(session_id)
#     try:
#         db_check = Chroma(
#             persist_directory=CHROMA_DIR,
#             embedding_function=embeddings,
#             collection_name=collection_name
#         )
#         if db_check.get()["ids"]:
#             db_check.delete_collection()
#             print(f"[INFO] Cleared old collection: {collection_name}")
#     except Exception as e:
#         print(f"[INFO] Will create fresh collection: {e}")

#     vector_store = Chroma.from_documents(
#         documents=final_chunks,
#         embedding=embeddings,
#         persist_directory=CHROMA_DIR,
#         collection_name=collection_name
#     )

#     print(f"[SUCCESS] Indexed {len(final_chunks)} chunks → '{collection_name}' [{provider}]")
#     return vector_store.as_retriever(search_kwargs={"k": 4})


# # ── Core: Query Document ───────────────────────────────────────────────────

# def query_document(session_id: str, query: str, api_key: str = None) -> str:
#     """
#     Retrieves relevant chunks from ChromaDB and queries the active LLM.

#     NOTE: api_key parameter is kept for backward-compat but IGNORED.
#     Keys are always read fresh from config at call time.
#     """
#     # ── Always read live values from config ───────────────────────────────
#     import config
#     provider     = config.ACTIVE_PROVIDER
#     live_api_key = config.get_active_api_key()
#     ollama_url   = config.OLLAMA_BASE_URL
#     model        = config.get_active_chat_model()

#     print(f"[INFO] Query | Provider: {provider} | Model: {model} | Session: {session_id}")
#     print(f"[INFO] API Key status: {'✓ present' if live_api_key else '✗ EMPTY'}")

#     # 1. Load vector store with live key
#     embeddings      = _get_embeddings(provider, live_api_key, ollama_url)
#     collection_name = clean_collection_name(session_id)

#     vector_store = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings,
#         collection_name=collection_name
#     )

#     # 2. Retrieve relevant chunks
#     docs = vector_store.as_retriever(search_kwargs={"k": 4}).invoke(query)

#     if not docs:
#         return (
#             "No relevant content found for your query.\n"
#             "Please verify the document was indexed successfully."
#         )

#     # 3. Format context with page references
#     context = "\n\n".join(
#         f"--- Source: {d.metadata.get('source', 'Document')}, "
#         f"Page: {d.metadata.get('page', 'N/A')} ---\n{d.page_content}"
#         for d in docs
#     )

#     # 4. Build prompt
#     system_prompt = (
#         "You are an expert document analysis assistant.\n"
#         "Answer the user's question using ONLY the provided context.\n"
#         "Each block starts with '--- Source: <file>, Page: <num> ---'.\n"
#         "Always cite page numbers in your answer, e.g. [Page 3].\n"
#         "If the answer is not in the context, say so clearly.\n\n"
#         "Context:\n{context}"
#     )
#     prompt    = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ])
#     formatted = prompt.format(context=context, input=query)

#     # 5. Query LLM with live key
#     llm      = _get_llm(provider, live_api_key, model, ollama_url)
#     response = llm.invoke(formatted)
#     return response.content

# Version 4

# # core/rag_engine.py
# import os
# import re

# from langchain_community.vectorstores import Chroma

# try:
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
# except ImportError:
#     from langchain.text_splitter import RecursiveCharacterTextSplitter

# try:
#     from langchain_core.documents import Document
# except ImportError:
#     from langchain.docstore.document import Document

# from langchain_core.prompts import ChatPromptTemplate
# from config import CHROMA_DIR
# from core.parser import parse_file


# # ── Provider Factory — Embeddings ──────────────────────────────────────────

# def _get_embeddings(provider: str, api_key: str,
#                     ollama_base_url: str = "http://localhost:11434"):
#     """
#     Returns the correct LangChain embedding object.
#     Key is also guaranteed to be in os.environ before this is called
#     (config._inject_env_vars handles that), but we pass it explicitly
#     as well so there is zero ambiguity.
#     """
#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open Settings → paste your key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import GoogleGenerativeAIEmbeddings
#         return GoogleGenerativeAIEmbeddings(
#             model="models/text-embedding-004",
#             google_api_key=api_key
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=api_key
#         )

#     elif provider == "Claude":
#         # Anthropic has no embedding model — we use OpenAI embeddings
#         import config as _cfg
#         openai_key = _cfg.OPENAI_API_KEY
#         if not openai_key:
#             raise ValueError(
#                 "Claude was selected as provider.\n"
#                 "Claude has no embedding model so DocuMind uses OpenAI for indexing.\n"
#                 "Please also set your OpenAI API key in Settings."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=openai_key
#         )

#     elif provider == "Ollama":
#         from langchain_community.embeddings import OllamaEmbeddings
#         return OllamaEmbeddings(
#             model="nomic-embed-text",
#             base_url=ollama_base_url
#         )

#     else:
#         raise ValueError(
#             f"Unknown provider: '{provider}'.\n"
#             "Supported: Gemini, OpenAI, Claude, Ollama."
#         )


# # ── Provider Factory — Chat LLM ────────────────────────────────────────────

# def _get_llm(provider: str, api_key: str, model: str,
#              ollama_base_url: str = "http://localhost:11434"):
#     """Returns the correct LangChain chat LLM for the active provider."""

#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open Settings → paste your key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         return ChatGoogleGenerativeAI(
#             model=model or "gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0.3,
#             convert_system_message_to_human=True
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import ChatOpenAI
#         return ChatOpenAI(
#             model=model or "gpt-4o",
#             openai_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Claude":
#         if not api_key:
#             raise ValueError(
#                 "Claude API key is not set.\n"
#                 "Open Settings → paste your Anthropic key → click ⚡ Apply Now."
#             )
#         from langchain_anthropic import ChatAnthropic
#         return ChatAnthropic(
#             model=model or "claude-sonnet-4-6",
#             anthropic_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Ollama":
#         from langchain_community.chat_models import ChatOllama
#         return ChatOllama(
#             model=model or "llama3",
#             base_url=ollama_base_url,
#             temperature=0.3
#         )

#     else:
#         raise ValueError(f"Unknown provider: '{provider}'.")


# # ── Collection Name Sanitizer ──────────────────────────────────────────────

# def clean_collection_name(session_id: str) -> str:
#     cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
#     if not cleaned[0].isalnum():
#         cleaned = "col_" + cleaned
#     return cleaned[:63]


# # ── Core: Index Document ───────────────────────────────────────────────────

# def process_and_index_doc(file_path: str, session_id: str, api_key: str = None):
#     """
#     Parses the document, chunks it, embeds with the active provider,
#     and stores in a session-specific ChromaDB collection.

#     NOTE: api_key parameter is kept for backward-compat but IGNORED.
#     Keys are always read fresh from config at call time so stale
#     lambda captures can never cause 'key not set' errors.
#     """
#     # ── Always read live values from config — never trust the passed-in key ──
#     import config
#     provider       = config.ACTIVE_PROVIDER
#     live_api_key   = config.get_active_api_key()
#     ollama_url     = config.OLLAMA_BASE_URL

#     print(f"[INFO] Indexing | Provider: {provider} | Session: {session_id} | File: {file_path}")
#     print(f"[INFO] API Key status: {'✓ present' if live_api_key else '✗ EMPTY'}")

#     # 1. Parse
#     parsed   = parse_file(file_path)
#     doc_name = os.path.basename(file_path)

#     documents = []
#     if parsed.get("pages"):
#         for p in parsed["pages"]:
#             documents.append(Document(
#                 page_content=p["text"],
#                 metadata={"page": p["page"], "source": doc_name}
#             ))
#     else:
#         documents.append(Document(
#             page_content=parsed.get("text", ""),
#             metadata={"page": 1, "source": doc_name}
#         ))

#     # 2. Chunk
#     splitter     = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     final_chunks = splitter.split_documents(documents)

#     # 3. Build embedding model using live key
#     embeddings = _get_embeddings(provider, live_api_key, ollama_url)

#     # 4. Wipe existing collection and re-index fresh
#     collection_name = clean_collection_name(session_id)
#     try:
#         db_check = Chroma(
#             persist_directory=CHROMA_DIR,
#             embedding_function=embeddings,
#             collection_name=collection_name
#         )
#         if db_check.get()["ids"]:
#             db_check.delete_collection()
#             print(f"[INFO] Cleared old collection: {collection_name}")
#     except Exception as e:
#         print(f"[INFO] Will create fresh collection: {e}")

#     vector_store = Chroma.from_documents(
#         documents=final_chunks,
#         embedding=embeddings,
#         persist_directory=CHROMA_DIR,
#         collection_name=collection_name
#     )

#     print(f"[SUCCESS] Indexed {len(final_chunks)} chunks → '{collection_name}' [{provider}]")
#     return vector_store.as_retriever(search_kwargs={"k": 4})


# # ── Core: Query Document ───────────────────────────────────────────────────

# def query_document(session_id: str, query: str, api_key: str = None) -> str:
#     """
#     Retrieves relevant chunks from ChromaDB and queries the active LLM.

#     NOTE: api_key parameter is kept for backward-compat but IGNORED.
#     Keys are always read fresh from config at call time.
#     """
#     # ── Always read live values from config ───────────────────────────────
#     import config
#     provider     = config.ACTIVE_PROVIDER
#     live_api_key = config.get_active_api_key()
#     ollama_url   = config.OLLAMA_BASE_URL
#     model        = config.get_active_chat_model()

#     print(f"[INFO] Query | Provider: {provider} | Model: {model} | Session: {session_id}")
#     print(f"[INFO] API Key status: {'✓ present' if live_api_key else '✗ EMPTY'}")

#     # 1. Load vector store with live key
#     embeddings      = _get_embeddings(provider, live_api_key, ollama_url)
#     collection_name = clean_collection_name(session_id)

#     vector_store = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings,
#         collection_name=collection_name
#     )

#     # 2. Retrieve relevant chunks
#     docs = vector_store.as_retriever(search_kwargs={"k": 4}).invoke(query)

#     if not docs:
#         return (
#             "No relevant content found for your query.\n"
#             "Please verify the document was indexed successfully."
#         )

#     # 3. Format context with page references
#     context = "\n\n".join(
#         f"--- Source: {d.metadata.get('source', 'Document')}, "
#         f"Page: {d.metadata.get('page', 'N/A')} ---\n{d.page_content}"
#         for d in docs
#     )

#     # 4. Build prompt
#     system_prompt = (
#         "You are an expert document analysis assistant.\n"
#         "Answer the user's question using ONLY the provided context.\n"
#         "Each block starts with '--- Source: <file>, Page: <num> ---'.\n"
#         "Always cite page numbers in your answer, e.g. [Page 3].\n"
#         "If the answer is not in the context, say so clearly.\n\n"
#         "Context:\n{context}"
#     )
#     prompt    = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ])
#     formatted = prompt.format(context=context, input=query)

#     # 5. Query LLM with live key
#     llm      = _get_llm(provider, live_api_key, model, ollama_url)
#     response = llm.invoke(formatted)
#     return response.content

# Version 5

# # core/rag_engine.py
# import os
# import re

# from langchain_community.vectorstores import Chroma

# try:
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
# except ImportError:
#     from langchain.text_splitter import RecursiveCharacterTextSplitter

# try:
#     from langchain_core.documents import Document
# except ImportError:
#     from langchain.docstore.document import Document

# from langchain_core.prompts import ChatPromptTemplate
# from config import CHROMA_DIR
# from core.parser import parse_file


# # ── Collection Name Sanitizer ──────────────────────────────────────────────

# def clean_collection_name(session_id: str) -> str:
#     cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
#     if not cleaned[0].isalnum():
#         cleaned = "col_" + cleaned
#     return cleaned[:63]


# # ── Provider Factory — Embeddings ──────────────────────────────────────────

# def _get_embeddings(provider: str, api_key: str,
#                     ollama_base_url: str = "http://localhost:11434"):
#     """
#     Returns the correct LangChain embedding object for the active provider.
#     Key is passed explicitly AND is already in os.environ (injected by config).
#     """
#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open ⚙ Settings → paste your Gemini key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import GoogleGenerativeAIEmbeddings
#         # gemini-embedding-001 is the current stable free-tier model
#         return GoogleGenerativeAIEmbeddings(
#             model="gemini-embedding-001",
#             google_api_key=api_key
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open ⚙ Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=api_key
#         )

#     elif provider == "Claude":
#         # Anthropic has no embedding model — fall back to OpenAI embeddings
#         import config as _cfg
#         openai_key = _cfg.OPENAI_API_KEY
#         if not openai_key:
#             raise ValueError(
#                 "Claude provider selected.\n"
#                 "Claude has no embedding model — DocuMind uses OpenAI for indexing.\n"
#                 "Please also set your OpenAI API key in Settings."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=openai_key
#         )

#     elif provider == "Ollama":
#         from langchain_community.embeddings import OllamaEmbeddings
#         return OllamaEmbeddings(
#             model="nomic-embed-text",
#             base_url=ollama_base_url
#         )

#     else:
#         raise ValueError(
#             f"Unknown provider: '{provider}'.\n"
#             "Supported options: Gemini, OpenAI, Claude, Ollama."
#         )


# # ── Provider Factory — Chat LLM ────────────────────────────────────────────

# def _get_llm(provider: str, api_key: str, model: str,
#              ollama_base_url: str = "http://localhost:11434"):
#     """Returns the correct LangChain chat LLM for the active provider."""

#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open ⚙ Settings → paste your Gemini key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         return ChatGoogleGenerativeAI(
#             model=model or "gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0.3,
#             convert_system_message_to_human=True
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open ⚙ Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import ChatOpenAI
#         return ChatOpenAI(
#             model=model or "gpt-4o",
#             openai_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Claude":
#         if not api_key:
#             raise ValueError(
#                 "Claude API key is not set.\n"
#                 "Open ⚙ Settings → paste your Anthropic key → click ⚡ Apply Now."
#             )
#         from langchain_anthropic import ChatAnthropic
#         return ChatAnthropic(
#             model=model or "claude-sonnet-4-6",
#             anthropic_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Ollama":
#         from langchain_community.chat_models import ChatOllama
#         return ChatOllama(
#             model=model or "llama3",
#             base_url=ollama_base_url,
#             temperature=0.3
#         )

#     else:
#         raise ValueError(f"Unknown provider: '{provider}'.")


# # ── Core: Index Document ───────────────────────────────────────────────────

# def process_and_index_doc(file_path: str, session_id: str, api_key: str = None):
#     """
#     Parses, chunks, embeds and stores the document in ChromaDB.
#     Always reads the live key from config — never uses the passed-in api_key.
#     This ensures keys set via Settings → Apply Now work immediately.
#     """
#     import config

#     provider     = config.ACTIVE_PROVIDER
#     live_key     = config.get_active_api_key()
#     ollama_url   = config.OLLAMA_BASE_URL

#     print(f"[INFO] Indexing | Provider: {provider} | Session: {session_id}")
#     print(f"[INFO] Key status: {'✓ present' if live_key else '✗ MISSING — set in Settings'}")

#     # 1. Parse file
#     parsed   = parse_file(file_path)
#     doc_name = os.path.basename(file_path)

#     documents = []
#     if parsed.get("pages"):
#         for p in parsed["pages"]:
#             documents.append(Document(
#                 page_content=p["text"],
#                 metadata={"page": p["page"], "source": doc_name}
#             ))
#     else:
#         documents.append(Document(
#             page_content=parsed.get("text", ""),
#             metadata={"page": 1, "source": doc_name}
#         ))

#     # 2. Chunk
#     splitter     = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     final_chunks = splitter.split_documents(documents)

#     # 3. Get embeddings using live key
#     embeddings = _get_embeddings(provider, live_key, ollama_url)

#     # 4. Clear old collection and re-index
#     collection_name = clean_collection_name(session_id)
#     try:
#         db_check = Chroma(
#             persist_directory=CHROMA_DIR,
#             embedding_function=embeddings,
#             collection_name=collection_name
#         )
#         if db_check.get()["ids"]:
#             db_check.delete_collection()
#             print(f"[INFO] Cleared old collection: {collection_name}")
#     except Exception as e:
#         print(f"[INFO] Creating fresh collection ({e})")

#     vector_store = Chroma.from_documents(
#         documents=final_chunks,
#         embedding=embeddings,
#         persist_directory=CHROMA_DIR,
#         collection_name=collection_name
#     )

#     print(f"[SUCCESS] Indexed {len(final_chunks)} chunks → '{collection_name}' [{provider}]")
#     return vector_store.as_retriever(search_kwargs={"k": 4})


# # ── Core: Query Document ───────────────────────────────────────────────────

# def query_document(session_id: str, query: str, api_key: str = None) -> str:
#     """
#     Retrieves relevant chunks and queries the active LLM.
#     Always reads the live key from config — never uses the passed-in api_key.
#     """
#     import config

#     provider   = config.ACTIVE_PROVIDER
#     live_key   = config.get_active_api_key()
#     ollama_url = config.OLLAMA_BASE_URL
#     model      = config.get_active_chat_model()

#     print(f"[INFO] Query | Provider: {provider} | Model: {model}")
#     print(f"[INFO] Key status: {'✓ present' if live_key else '✗ MISSING'}")

#     # 1. Load vector store
#     embeddings      = _get_embeddings(provider, live_key, ollama_url)
#     collection_name = clean_collection_name(session_id)

#     vector_store = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings,
#         collection_name=collection_name
#     )

#     # 2. Retrieve chunks
#     docs = vector_store.as_retriever(search_kwargs={"k": 4}).invoke(query)

#     if not docs:
#         return (
#             "No relevant content found for your query.\n"
#             "Please verify the document was indexed successfully."
#         )

#     # 3. Format context
#     context = "\n\n".join(
#         f"--- Source: {d.metadata.get('source', 'Document')}, "
#         f"Page: {d.metadata.get('page', 'N/A')} ---\n{d.page_content}"
#         for d in docs
#     )

#     # 4. Build and send prompt
#     system_prompt = (
#         "You are an expert document analysis assistant.\n"
#         "Answer the user's question using ONLY the provided context.\n"
#         "Each block starts with '--- Source: <file>, Page: <num> ---'.\n"
#         "Always cite page numbers in your answer, e.g. [Page 3].\n"
#         "If the answer is not in the context, say so clearly.\n\n"
#         "Context:\n{context}"
#     )
#     prompt    = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ])
#     formatted = prompt.format(context=context, input=query)
#     llm       = _get_llm(provider, live_key, model, ollama_url)
#     response  = llm.invoke(formatted)
#     return response.content

# Version: 6

# # core/rag_engine.py
# import os
# import re

# try:
#     from langchain_chroma import Chroma
# except ImportError:
#     from langchain_community.vectorstores import Chroma

# try:
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
# except ImportError:
#     from langchain.text_splitter import RecursiveCharacterTextSplitter

# try:
#     from langchain_core.documents import Document
# except ImportError:
#     from langchain.docstore.document import Document

# from langchain_core.prompts import ChatPromptTemplate
# from config import CHROMA_DIR
# from core.parser import parse_file


# # ── Collection Name Sanitizer ──────────────────────────────────────────────

# def clean_collection_name(session_id: str) -> str:
#     cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
#     if not cleaned[0].isalnum():
#         cleaned = "col_" + cleaned
#     return cleaned[:63]


# # ── Provider Factory — Embeddings ──────────────────────────────────────────

# def _get_embeddings(provider: str, api_key: str,
#                     ollama_base_url: str = "http://localhost:11434"):
#     """
#     Returns the correct LangChain embedding object for the active provider.
#     Key is passed explicitly AND is already in os.environ (injected by config).
#     """
#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open ⚙ Settings → paste your Gemini key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import GoogleGenerativeAIEmbeddings
#         # gemini-embedding-001 is the current stable free-tier model
#         return GoogleGenerativeAIEmbeddings(
#             model="gemini-embedding-001",
#             google_api_key=api_key
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open ⚙ Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=api_key
#         )

#     elif provider == "Claude":
#         # Anthropic has no embedding model — fall back to OpenAI embeddings
#         import config as _cfg
#         openai_key = _cfg.OPENAI_API_KEY
#         if not openai_key:
#             raise ValueError(
#                 "Claude provider selected.\n"
#                 "Claude has no embedding model — DocuMind uses OpenAI for indexing.\n"
#                 "Please also set your OpenAI API key in Settings."
#             )
#         from langchain_openai import OpenAIEmbeddings
#         return OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=openai_key
#         )

#     elif provider == "Ollama":
#         from langchain_community.embeddings import OllamaEmbeddings
#         return OllamaEmbeddings(
#             model="nomic-embed-text",
#             base_url=ollama_base_url
#         )

#     else:
#         raise ValueError(
#             f"Unknown provider: '{provider}'.\n"
#             "Supported options: Gemini, OpenAI, Claude, Ollama."
#         )


# # ── Provider Factory — Chat LLM ────────────────────────────────────────────

# def _get_llm(provider: str, api_key: str, model: str,
#              ollama_base_url: str = "http://localhost:11434"):
#     """Returns the correct LangChain chat LLM for the active provider."""

#     if provider == "Gemini":
#         if not api_key:
#             raise ValueError(
#                 "Gemini API key is not set.\n"
#                 "Open ⚙ Settings → paste your Gemini key → click ⚡ Apply Now."
#             )
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         return ChatGoogleGenerativeAI(
#             model=model or "gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0.3,
#             convert_system_message_to_human=True
#         )

#     elif provider == "OpenAI":
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key is not set.\n"
#                 "Open ⚙ Settings → paste your OpenAI key → click ⚡ Apply Now."
#             )
#         from langchain_openai import ChatOpenAI
#         return ChatOpenAI(
#             model=model or "gpt-4o",
#             openai_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Claude":
#         if not api_key:
#             raise ValueError(
#                 "Claude API key is not set.\n"
#                 "Open ⚙ Settings → paste your Anthropic key → click ⚡ Apply Now."
#             )
#         from langchain_anthropic import ChatAnthropic
#         return ChatAnthropic(
#             model=model or "claude-sonnet-4-6",
#             anthropic_api_key=api_key,
#             temperature=0.3
#         )

#     elif provider == "Ollama":
#         from langchain_community.chat_models import ChatOllama
#         return ChatOllama(
#             model=model or "llama3",
#             base_url=ollama_base_url,
#             temperature=0.3
#         )

#     else:
#         raise ValueError(f"Unknown provider: '{provider}'.")


# # ── Core: Index Document ───────────────────────────────────────────────────

# def process_and_index_doc(file_path: str, session_id: str, api_key: str = None):
#     """
#     Parses, chunks, embeds and stores the document in ChromaDB.
#     Always reads the live key from config — never uses the passed-in api_key.
#     This ensures keys set via Settings → Apply Now work immediately.
#     """
#     import config

#     provider     = config.ACTIVE_PROVIDER
#     live_key     = config.get_active_api_key()
#     ollama_url   = config.OLLAMA_BASE_URL

#     print(f"[INFO] Indexing | Provider: {provider} | Session: {session_id}")
#     print(f"[INFO] Key status: {'✓ present' if live_key else '✗ MISSING — set in Settings'}")

#     # 1. Parse file
#     parsed   = parse_file(file_path)
#     doc_name = os.path.basename(file_path)

#     documents = []
#     if parsed.get("pages"):
#         for p in parsed["pages"]:
#             documents.append(Document(
#                 page_content=p["text"],
#                 metadata={"page": p["page"], "source": doc_name}
#             ))
#     else:
#         documents.append(Document(
#             page_content=parsed.get("text", ""),
#             metadata={"page": 1, "source": doc_name}
#         ))

#     # 2. Chunk
#     splitter     = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     final_chunks = splitter.split_documents(documents)

#     # 3. Get embeddings using live key
#     embeddings = _get_embeddings(provider, live_key, ollama_url)

#     # 4. Clear old collection and re-index
#     collection_name = clean_collection_name(session_id)
#     try:
#         db_check = Chroma(
#             persist_directory=CHROMA_DIR,
#             embedding_function=embeddings,
#             collection_name=collection_name
#         )
#         if db_check.get()["ids"]:
#             db_check.delete_collection()
#             print(f"[INFO] Cleared old collection: {collection_name}")
#     except Exception as e:
#         print(f"[INFO] Creating fresh collection ({e})")

#     vector_store = Chroma.from_documents(
#         documents=final_chunks,
#         embedding=embeddings,
#         persist_directory=CHROMA_DIR,
#         collection_name=collection_name
#     )

#     print(f"[SUCCESS] Indexed {len(final_chunks)} chunks → '{collection_name}' [{provider}]")
#     return vector_store.as_retriever(search_kwargs={"k": 4})


# # ── Core: Query Document ───────────────────────────────────────────────────

# def query_document(session_id: str, query: str, api_key: str = None) -> str:
#     """
#     Retrieves relevant chunks and queries the active LLM.
#     Always reads the live key from config — never uses the passed-in api_key.
#     """
#     import config

#     provider   = config.ACTIVE_PROVIDER
#     live_key   = config.get_active_api_key()
#     ollama_url = config.OLLAMA_BASE_URL
#     model      = config.get_active_chat_model()

#     print(f"[INFO] Query | Provider: {provider} | Model: {model}")
#     print(f"[INFO] Key status: {'✓ present' if live_key else '✗ MISSING'}")

#     # 1. Load vector store
#     embeddings      = _get_embeddings(provider, live_key, ollama_url)
#     collection_name = clean_collection_name(session_id)

#     vector_store = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings,
#         collection_name=collection_name
#     )

#     # 2. Retrieve chunks
#     docs = vector_store.as_retriever(search_kwargs={"k": 4}).invoke(query)

#     if not docs:
#         return (
#             "No relevant content found for your query.\n"
#             "Please verify the document was indexed successfully."
#         )

#     # 3. Format context
#     context = "\n\n".join(
#         f"--- Source: {d.metadata.get('source', 'Document')}, "
#         f"Page: {d.metadata.get('page', 'N/A')} ---\n{d.page_content}"
#         for d in docs
#     )

#     # 4. Build and send prompt
#     system_prompt = (
#         "You are an expert document analysis assistant.\n"
#         "Answer the user's question using ONLY the provided context.\n"
#         "Each block starts with '--- Source: <file>, Page: <num> ---'.\n"
#         "Always cite page numbers in your answer, e.g. [Page 3].\n"
#         "If the answer is not in the context, say so clearly.\n\n"
#         "Context:\n{context}"
#     )
#     prompt    = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ])
#     formatted = prompt.format(context=context, input=query)
#     llm       = _get_llm(provider, live_key, model, ollama_url)
#     response  = llm.invoke(formatted)
#     return response.content

# Version 7

# core/rag_engine.py
import os
import re

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_core.prompts import ChatPromptTemplate
from config import CHROMA_DIR
from core.parser import parse_file


# ── Collection Name Sanitizer ──────────────────────────────────────────────

def clean_collection_name(session_id: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
    if not cleaned[0].isalnum():
        cleaned = "col_" + cleaned
    return cleaned[:63]


# ── Provider Factory — Embeddings ──────────────────────────────────────────

def _get_embeddings(provider: str, api_key: str,
                    ollama_base_url: str = "http://localhost:11434"):
    """
    Returns the correct LangChain embedding object for the active provider.
    Key is passed explicitly AND is already in os.environ (injected by config).
    """
    if provider == "Gemini":
        if not api_key:
            raise ValueError(
                "Gemini API key is not set.\n"
                "Open ⚙ Settings → paste your Gemini key → click ⚡ Apply Now."
            )
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        # gemini-embedding-001 is the current stable free-tier model
        return GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=api_key
        )

    elif provider == "OpenAI":
        if not api_key:
            raise ValueError(
                "OpenAI API key is not set.\n"
                "Open ⚙ Settings → paste your OpenAI key → click ⚡ Apply Now."
            )
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key
        )

    elif provider == "Claude":
        # Anthropic has no embedding model — fall back to OpenAI embeddings
        import config as _cfg
        openai_key = _cfg.OPENAI_API_KEY
        if not openai_key:
            raise ValueError(
                "Claude provider selected.\n"
                "Claude has no embedding model — DocuMind uses OpenAI for indexing.\n"
                "Please also set your OpenAI API key in Settings."
            )
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_key
        )

    elif provider == "Ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=ollama_base_url
        )

    else:
        raise ValueError(
            f"Unknown provider: '{provider}'.\n"
            "Supported options: Gemini, OpenAI, Claude, Ollama."
        )


# ── Provider Factory — Chat LLM ────────────────────────────────────────────

def _get_llm(provider: str, api_key: str, model: str,
             ollama_base_url: str = "http://localhost:11434"):
    """Returns the correct LangChain chat LLM for the active provider."""

    if provider == "Gemini":
        if not api_key:
            raise ValueError(
                "Gemini API key is not set.\n"
                "Open ⚙ Settings → paste your Gemini key → click ⚡ Apply Now."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True
        )

    elif provider == "OpenAI":
        if not api_key:
            raise ValueError(
                "OpenAI API key is not set.\n"
                "Open ⚙ Settings → paste your OpenAI key → click ⚡ Apply Now."
            )
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4o",
            openai_api_key=api_key,
            temperature=0.3
        )

    elif provider == "Claude":
        if not api_key:
            raise ValueError(
                "Claude API key is not set.\n"
                "Open ⚙ Settings → paste your Anthropic key → click ⚡ Apply Now."
            )
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-sonnet-4-6",
            anthropic_api_key=api_key,
            temperature=0.3
        )

    elif provider == "Ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=model or "llama3",
            base_url=ollama_base_url,
            temperature=0.3
        )

    else:
        raise ValueError(f"Unknown provider: '{provider}'.")


# ── Core: Index Document ───────────────────────────────────────────────────

def process_and_index_doc(file_path: str, session_id: str, api_key: str = None):
    """
    Parses, chunks, embeds and stores the document in ChromaDB.
    Always reads the live key from config — never uses the passed-in api_key.
    This ensures keys set via Settings → Apply Now work immediately.
    """
    import config

    provider     = config.ACTIVE_PROVIDER
    live_key     = config.get_active_api_key()
    ollama_url   = config.OLLAMA_BASE_URL

    print(f"[INFO] Indexing | Provider: {provider} | Session: {session_id}")
    print(f"[INFO] Key status: {'✓ present' if live_key else '✗ MISSING — set in Settings'}")

    # 1. Parse file
    parsed   = parse_file(file_path)
    doc_name = os.path.basename(file_path)

    documents = []
    if parsed.get("pages"):
        for p in parsed["pages"]:
            documents.append(Document(
                page_content=p["text"],
                metadata={"page": p["page"], "source": doc_name}
            ))
    else:
        documents.append(Document(
            page_content=parsed.get("text", ""),
            metadata={"page": 1, "source": doc_name}
        ))

    # 2. Chunk
    splitter     = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_chunks = splitter.split_documents(documents)

    # 3. Get embeddings using live key
    embeddings = _get_embeddings(provider, live_key, ollama_url)

    # 4. Clear old collection and re-index
    collection_name = clean_collection_name(session_id)
    try:
        db_check = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        if db_check.get()["ids"]:
            db_check.delete_collection()
            print(f"[INFO] Cleared old collection: {collection_name}")
    except Exception as e:
        print(f"[INFO] Creating fresh collection ({e})")

    vector_store = Chroma.from_documents(
        documents=final_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=collection_name
    )

    print(f"[SUCCESS] Indexed {len(final_chunks)} chunks → '{collection_name}' [{provider}]")
    return vector_store.as_retriever(search_kwargs={"k": 4})


# ── Core: Query Document ───────────────────────────────────────────────────

def query_document(session_id: str, query: str, api_key: str = None) -> str:
    """
    Retrieves relevant chunks and queries the active LLM.
    Always reads the live key from config — never uses the passed-in api_key.
    """
    import config

    provider   = config.ACTIVE_PROVIDER
    live_key   = config.get_active_api_key()
    ollama_url = config.OLLAMA_BASE_URL
    model      = config.get_active_chat_model()

    print(f"[INFO] Query | Provider: {provider} | Model: {model}")
    print(f"[INFO] Key status: {'✓ present' if live_key else '✗ MISSING'}")

    # 1. Load vector store
    embeddings      = _get_embeddings(provider, live_key, ollama_url)
    collection_name = clean_collection_name(session_id)

    vector_store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    # 2. Retrieve chunks
    docs = vector_store.as_retriever(search_kwargs={"k": 4}).invoke(query)

    if not docs:
        return (
            "No relevant content found for your query.\n"
            "Please verify the document was indexed successfully."
        )

    # 3. Format context
    context = "\n\n".join(
        f"--- Source: {d.metadata.get('source', 'Document')}, "
        f"Page: {d.metadata.get('page', 'N/A')} ---\n{d.page_content}"
        for d in docs
    )

    # 4. Build and send prompt
    system_prompt = (
        "You are an expert document analysis assistant.\n"
        "Answer the user's question using ONLY the provided context.\n"
        "Each block starts with '--- Source: <file>, Page: <num> ---'.\n"
        "Always cite page numbers in your answer, e.g. [Page 3].\n"
        "If the answer is not in the context, say so clearly.\n\n"
        "Context:\n{context}"
    )
    prompt    = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    formatted = prompt.format(context=context, input=query)
    llm       = _get_llm(provider, live_key, model, ollama_url)
    response  = llm.invoke(formatted)
    return response.content