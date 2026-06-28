# core/agent_flow.py
import os
import time
from typing import TypedDict, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
try:
    from langgraph.graph import START, END
    HAS_START_END = True
except ImportError:
    START = "__start__"
    END = "__end__"
    HAS_START_END = False

# Import Parsers and DB Ops
from core.parser import parse_file
from core.db_ops import execute_differential_upsert, export_to_excel, write_audit_log

# Pydantic Schemas for Schema Discovery Node

class ColumnDefinition(BaseModel):
    name: str = Field(description="Name of the column. Use lowercase snake_case.")
    type: str = Field(description="Data type of the column. Choose from: INTEGER, VARCHAR, FLOAT, BOOLEAN")
    description: str = Field(description="Brief explanation of the column meaning")
    primary_key: bool = Field(description="Whether this column is a primary key or key identifier")

class DiscoveredSchema(BaseModel):
    schema_name: str = Field(description="A suitable SQL table name for this dataset (e.g. employee_records, invoices, logs)")
    columns: List[ColumnDefinition] = Field(description="List of all fields/columns in the table")
    composite_keys: List[str] = Field(description="List of column names that form a composite key or identifier for upsert checks")

# LangGraph Pipeline State Definition

class PipelineState(TypedDict):
    file_path: str
    file_type: str
    raw_content: dict
    schema_name: str
    discovered_schema: dict
    extracted_data: list
    validation_errors: list
    retry_count: int
    tokens_used: int
    execution_start_time: float
    export_path: str
    status: str
    database_upsert_stats: dict
    error_message: str

# Helper to construct dynamic JSON schemas for the extraction step

def build_extraction_json_schema(discovered_schema: dict) -> dict:
    """Builds a JSON Schema dictionary for ChatGoogleGenerativeAI's with_structured_output."""
    properties = {}
    required = []
    
    for col in discovered_schema.get("columns", []):
        col_name = col["name"].lower().strip()
        col_type = col["type"].upper()
        
        if "INT" in col_type:
            js_type = "integer"
        elif "FLOAT" in col_type or "NUM" in col_type or "DOUBLE" in col_type or "DEC" in col_type:
            js_type = "number"
        elif "BOOL" in col_type:
            js_type = "boolean"
        else:
            js_type = "string"
            
        properties[col_name] = {
            "type": js_type,
            "description": col.get("description", f"Value for {col_name}")
        }
        required.append(col_name)
        
    return {
        "type": "object",
        "properties": {
            "records": {
                "type": "array",
                "description": "List of all structured records extracted from the document",
                "items": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        },
        "required": ["records"]
    }

# LangGraph Nodes

def parse_node(state: PipelineState) -> dict:
    print("[NODE] Starting parse_node")
    start_time = time.time()
    file_path = state.get("file_path", "")
    file_type = state.get("file_type", "")
    
    # Handle direct database extraction vs files
    if file_type.lower() == "mysql" or file_type.lower() == "relational":
        from config import MYSQL_URL
        conn_url = state.get("connection_url", MYSQL_URL)
        table_name = state.get("schema_name", "mysql_table")
        raw_data = parse_file(file_path="", db_table_name=table_name, connection_url=conn_url)
    else:
        raw_data = parse_file(file_path)
        
    return {
        "raw_content": raw_data,
        "file_type": raw_data.get("format", file_type),
        "execution_start_time": start_time,
        "retry_count": 0,
        "validation_errors": [],
        "status": "PARSED"
    }

def schema_discovery_node(state: PipelineState) -> dict:
    print("[NODE] Starting schema_discovery_node")
    from config import GEMINI_API_KEY
    
    raw_content = state["raw_content"]
    text_sample = raw_content.get("text", "")
    
    # Tabular sheets already have columns; skip complex discovery and pre-populate structure
    if raw_content["type"] == "tabular":
        columns = [
            {"name": col, "type": "VARCHAR", "description": f"Tabular column {col}", "primary_key": (i == 0)}
            for i, col in enumerate(raw_content["columns"])
        ]
        schema_dict = {
            "schema_name": "tabular_export",
            "columns": columns,
            "composite_keys": [raw_content["columns"][0]]
        }
        print("[INFO] Tabular schema discovered directly from Pandas columns.")
        return {
            "schema_name": "tabular_export",
            "discovered_schema": schema_dict,
            "status": "SCHEMA_DISCOVERED"
        }
        
    # Limit text sample to avoid blowing up context window
    if len(text_sample) > 8000:
        text_sample = text_sample[:8000] + "\n... [TRUNCATED] ..."
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        convert_system_message_to_human=True
    )
    
    structured_llm = llm.with_structured_output(DiscoveredSchema)
    
    prompt = (
        "Analyze the following document context and suggest a structured database table schema "
        "that matches its fields. Determine what the data represents (e.g., invoices, user directory, logs) "
        "and map it to columns with types (INTEGER, VARCHAR, FLOAT, BOOLEAN).\n\n"
        "Document Sample:\n"
        f"{text_sample}"
    )
    
    discovered = structured_llm.invoke(prompt)
    
    schema_dict = {
        "schema_name": discovered.schema_name,
        "columns": [col.model_dump() for col in discovered.columns],
        "composite_keys": discovered.composite_keys
    }
    
    print(f"[SUCCESS] Discovered schema name: {discovered.schema_name}")
    return {
        "schema_name": discovered.schema_name,
        "discovered_schema": schema_dict,
        "status": "SCHEMA_DISCOVERED"
    }

def data_extraction_node(state: PipelineState) -> dict:
    print("[NODE] Starting data_extraction_node")
    from config import GEMINI_API_KEY
    
    raw_content = state["raw_content"]
    schema = state["discovered_schema"]
    
    # Build dynamic extraction schema structure
    extraction_schema = build_extraction_json_schema(schema)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.0,
        convert_system_message_to_human=True
    )
    
    structured_llm = llm.with_structured_output(extraction_schema)
    
    text_content = raw_content.get("text", "")
    if raw_content["type"] in ["tabular", "relational"]:
        # If already tabular, pass raw records straight for formatting/extraction validation
        import json
        text_content = f"JSON Tabular Data:\n{json.dumps(raw_content.get('data', []))}"
        
    prompt = (
        "Extract all records from the document and match them to the target schema fields. "
        "Convert values to the appropriate types (integers, floats, booleans, strings) as required.\n\n"
        f"Target Schema:\n{schema}\n\n"
        f"Content:\n{text_content}"
    )
    
    result = structured_llm.invoke(prompt)
    extracted = result.get("records", [])
    
    print(f"[SUCCESS] Extracted {len(extracted)} records from LLM.")
    return {
        "extracted_data": extracted,
        "status": "DATA_EXTRACTED"
    }

def validation_node(state: PipelineState) -> dict:
    print("[NODE] Starting validation_node")
    schema = state["discovered_schema"]
    records = state["extracted_data"]
    
    errors = []
    validated_records = []
    
    for idx, rec in enumerate(records):
        clean_rec = {}
        for col in schema.get("columns", []):
            col_name = col["name"].lower().strip()
            col_type = col["type"].upper()
            is_pk = col.get("primary_key", False) or col_name in schema.get("composite_keys", [])
            
            # Fetch values matching keys by original case or lowercase
            val = rec.get(col["name"])
            if val is None:
                val = rec.get(col_name)
                
            if val is None:
                if is_pk:
                    errors.append(f"Record {idx}: Missing value for primary/composite key '{col_name}'")
                clean_rec[col_name] = None
                continue
                
            # Perform validation and data type casting
            try:
                # Remove common numeric markers like dollar signs, commas
                cleaned_str = str(val).replace("$", "").replace(",", "").strip()
                
                if "INT" in col_type:
                    clean_rec[col_name] = int(float(cleaned_str))
                elif "FLOAT" in col_type or "NUM" in col_type or "DOUBLE" in col_type or "DEC" in col_type:
                    clean_rec[col_name] = float(cleaned_str)
                elif "BOOL" in col_type:
                    s_val = str(val).lower().strip()
                    if s_val in ["true", "1", "yes", "y", "t"]:
                        clean_rec[col_name] = True
                    elif s_val in ["false", "0", "no", "n", "f"]:
                        clean_rec[col_name] = False
                    else:
                        clean_rec[col_name] = bool(val)
                else:
                    clean_rec[col_name] = str(val)
            except Exception as cast_err:
                errors.append(f"Record {idx}: Column '{col_name}' value '{val}' cannot be cast to {col_type}: {cast_err}")
                clean_rec[col_name] = val
                
        validated_records.append(clean_rec)
        
    print(f"[INFO] Validation complete. Errors found: {len(errors)}")
    return {
        "extracted_data": validated_records,
        "validation_errors": errors,
        "status": "VALIDATED"
    }

def self_healing_node(state: PipelineState) -> dict:
    print(f"[NODE] Starting self_healing_node (Retry Count: {state.get('retry_count', 0)})")
    from config import GEMINI_API_KEY
    
    schema = state["discovered_schema"]
    records = state["extracted_data"]
    errors = state["validation_errors"]
    retry = state.get("retry_count", 0) + 1
    
    extraction_schema = build_extraction_json_schema(schema)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.0,
        convert_system_message_to_human=True
    )
    
    structured_llm = llm.with_structured_output(extraction_schema)
    
    errors_text = "\n".join(f" - {err}" for err in errors)
    
    prompt = (
        "You are a data validation self-healing engine. The previously extracted JSON records "
        "failed database constraints and validations with the following errors:\n"
        f"{errors_text}\n\n"
        "Your task is to correct the data in the records so they strictly conform to the schema types "
        "and resolve all errors. If an ID or required key is missing, generate a suitable unique key or deduce it "
        "from the context. If a float/int column has invalid formatting (e.g. currency signs, text), "
        "clean it to a pure number.\n\n"
        f"Target Schema:\n{schema}\n\n"
        f"Corrupted Records:\n{records}"
    )
    
    result = structured_llm.invoke(prompt)
    corrected = result.get("records", [])
    
    return {
        "extracted_data": corrected,
        "retry_count": retry,
        "status": "HEALED",
        "validation_errors": []  # Reset validation errors for next validation run
    }

def upsert_node(state: PipelineState) -> dict:
    print("[NODE] Starting upsert_node")
    
    schema = state["discovered_schema"]
    records = state["extracted_data"]
    file_path = state.get("file_path", "")
    file_name = os.path.basename(file_path) if file_path else state.get("schema_name", "database_import")
    file_type = state.get("file_type", "unknown")
    
    val_errors = state.get("validation_errors", [])
    status = "SUCCESS" if not val_errors else "PARTIAL_SUCCESS"
    err_msg = "; ".join(val_errors) if val_errors else None
    
    # Perform Dynamic DB Upsert
    stats = execute_differential_upsert(schema["schema_name"], schema, records)
    
    # Export flat Excel output
    excel_filename = f"{schema['schema_name']}_{int(time.time())}.xlsx"
    export_path = export_to_excel(records, excel_filename)
    
    start_time = state.get("execution_start_time")
    elapsed_ms = int((time.time() - start_time) * 1000) if start_time else 0
    
    total = stats["total"]
    success_rate = ((total - stats["failed"]) / total * 100.0) if total > 0 else 100.0
    if val_errors:
        success_rate = max(0.0, success_rate - 20.0)
        
    # Write execution trace to operational audit log
    write_audit_log(
        doc_name=file_name,
        doc_type=file_type,
        tokens=0, # Estimated
        time_ms=elapsed_ms,
        success_rate=success_rate,
        status=status,
        errors=err_msg
    )
    
    return {
        "database_upsert_stats": stats,
        "export_path": export_path,
        "status": "COMPLETED",
        "error_message": err_msg
    }

# LangGraph Conditional Router

def route_validation(state: PipelineState) -> str:
    errors = state.get("validation_errors", [])
    retry_count = state.get("retry_count", 0)
    
    if not errors:
        return "upsert"
    elif retry_count < 3:
        print(f"[ROUTER] Validation failed. Routing to self_healing. Attempt: {retry_count + 1}")
        return "heal"
    else:
        print("[ROUTER] Validation failed. Max retries reached. Routing directly to upsert.")
        return "upsert"

# Build compiled state machine

def build_agent_graph():
    workflow = StateGraph(PipelineState)
    
    # Register Nodes
    workflow.add_node("parse", parse_node)
    workflow.add_node("discover_schema", schema_discovery_node)
    workflow.add_node("extract_data", data_extraction_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("heal", self_healing_node)
    workflow.add_node("upsert", upsert_node)
    
    # Establish Edges
    if HAS_START_END:
        workflow.add_edge(START, "parse")
    else:
        workflow.set_entry_point("parse")
        
    workflow.add_edge("parse", "discover_schema")
    workflow.add_edge("discover_schema", "extract_data")
    workflow.add_edge("extract_data", "validate")
    
    # Conditional Routing
    workflow.add_conditional_edges(
        "validate",
        route_validation,
        {
            "upsert": "upsert",
            "heal": "heal"
        }
    )
    
    workflow.add_edge("heal", "validate")
    
    if HAS_START_END:
        workflow.add_edge("upsert", END)
    else:
        workflow.set_finish_point("upsert")
    
    return workflow.compile()
