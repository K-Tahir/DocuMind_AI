# test_run_agentic.py
import asyncio
import os
import sys
from core.agent_flow import build_agent_graph

async def main():
    print("[INFO] Starting End-to-End Agentic Pipeline Test...")
    
    # Check if test file exists
    test_pdf = "AssignmentWebScraperIntern.pdf"
    if not os.path.exists(test_pdf):
        print(f"[ERROR] Test PDF '{test_pdf}' not found in workspace.")
        return
        
    # Build compiled state machine
    print("[INFO] Building LangGraph Workflow Graph...")
    try:
        graph = build_agent_graph()
        print("[SUCCESS] Graph compiled successfully.")
    except Exception as e:
        print(f"[ERROR] Graph compilation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Run the graph
    initial_state = {
        "file_path": test_pdf,
        "file_type": "pdf",
        "retry_count": 0
    }
    
    print("[INFO] Invoking pipeline. This will parse, discover schema, extract, validate, upsert, and export...")
    try:
        result = await graph.ainvoke(initial_state)
        print("\n=== PIPELINE RUN COMPLETE ===")
        print(f"Final Status: {result.get('status')}")
        print(f"Schema Discovered: {result.get('schema_name')}")
        print(f"Discovered Columns: {[c['name'] for c in result.get('discovered_schema', {}).get('columns', [])]}")
        print(f"Records Extracted: {len(result.get('extracted_data', []))}")
        print(f"Database Stats: {result.get('database_upsert_stats')}")
        print(f"Excel Export Location: {result.get('export_path')}")
        print(f"Validation Errors: {result.get('validation_errors')}")
        print(f"Self-Healing Retries: {result.get('retry_count')}")
        print(f"Self-Healing Error Message: {result.get('error_message')}")
        print("=============================\n")
    except Exception as e:
        import traceback
        print("\n=== PIPELINE EXECUTION FAILURE ===")
        traceback.print_exc()
        print("==================================\n")

if __name__ == "__main__":
    # On Windows, set Event Loop policy for FastAPI/asyncio compatibility if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
