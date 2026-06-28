# test_run.py
import os
from storage.database import init_db, create_session, log_message
from core.parser import extract_pdf_pages
from core.rag_engine import process_and_index_doc, query_document
# 
# 1. Initialize our SQLite structures
init_db()

# 2. Setup testing variables
API_KEY = "AQ.Ab8RN6J_zI5KE4wCC8jEEsAS7Zt4hXy7EwQv31pfoZ5PdD9bIQ" # <- Replace with your key
TEST_PDF = "AssignmentWebScraperIntern.pdf"           # <- Replace with a local PDF filename
SESSION_ID = "session_001"

if API_KEY == "YOUR_ACTUAL_GEMINI_API_KEY_HERE" or not os.path.exists(TEST_PDF):
    print(f"[ERROR] Please ensure your API key is set and '{TEST_PDF}' exists in this folder.")
else:

# if API_KEY == "AQ.Ab8RN6La9qB6wFO9_B7UYILVecCldN8UfeumXGiKYWRJHDn9-g" or not os.path.exists(TEST_PDF):
#     print("[ERROR] Please update test_run.py with your real API key and a valid test PDF file path!")
# else:
    # 3. Create a session entry in SQLite
    create_session(SESSION_ID, TEST_PDF)
    
    # 4. Extract and Index
    pages = extract_pdf_pages(TEST_PDF)
    retriever = process_and_index_doc(pages, API_KEY)
    
    # 5. Ask a question!
    query = "Give me a summary of this document in 5 bullet points."
    print(f"\n[USER]: {query}")
    
    answer = query_document(retriever, query, API_KEY)
    print(f"\n[AI]: {answer}")
    
    # 6. Log the transaction to history
    log_message(SESSION_ID, "user", query)
    log_message(SESSION_ID, "ai", answer)
    print("\n[SUCCESS] Pipeline test complete. Everything saved to SQLite & Chroma DB.")