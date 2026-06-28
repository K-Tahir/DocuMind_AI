# core/db_ops.py
import os
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, 
    DateTime, inspect, text, select
)
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL, EXPORT_DIR

# Declarative base for standard tables
Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_name = Column(String(255))
    document_type = Column(String(50))
    tokens_used = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    parsing_success_rate = Column(Float, default=100.0)
    status = Column(String(50))
    errors = Column(String(1000), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Engine & Session Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_audit_db():
    """Ensure the audit log table exists in the target database."""
    Base.metadata.create_all(bind=engine)
    print(f"[INFO] Audit tables initialized on: {DATABASE_URL}")

# Auto-initialize database tables at module load time
init_audit_db()

def write_audit_log(doc_name: str, doc_type: str, tokens: int, time_ms: int, success_rate: float, status: str, errors: str = None):
    """Writes an execution trace entry to the audit logs."""
    db = SessionLocal()
    try:
        log_entry = AuditLog(
            document_name=doc_name,
            document_type=doc_type,
            tokens_used=tokens,
            execution_time_ms=time_ms,
            parsing_success_rate=success_rate,
            status=status,
            errors=errors,
            timestamp=datetime.now()
        )
        db.add(log_entry)
        db.commit()
        print(f"[SUCCESS] Audit log written for {doc_name} (Status: {status})")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to write audit log: {e}")
    finally:
        db.close()

def get_audit_logs() -> list[dict]:
    """Retrieves all audit logs as list of dicts."""
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        return [
            {
                "id": log.id,
                "document_name": log.document_name,
                "document_type": log.document_type,
                "tokens_used": log.tokens_used,
                "execution_time_ms": log.execution_time_ms,
                "parsing_success_rate": log.parsing_success_rate,
                "status": log.status,
                "errors": log.errors,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            } for log in logs
        ]
    except Exception as e:
        print(f"[ERROR] Failed to fetch audit logs: {e}")
        return []
    finally:
        db.close()

# Dynamic DB Ops

def map_type_string_to_sqlalchemy(type_str: str):
    """Maps custom string data types to SQLAlchemy column types."""
    type_str = str(type_str).upper()
    if "INT" in type_str:
        return Integer
    elif "FLOAT" in type_str or "NUM" in type_str or "DOUBLE" in type_str or "DEC" in type_str:
        return Float
    elif "BOOL" in type_str:
        return Boolean
    elif "DATE" in type_str or "TIME" in type_str:
        return String(100) # Keep date/time formats as strings for simplicity
    else:
        return String(500) # Fallback to standard string representation

def get_or_create_dynamic_table(table_name: str, schema_def: dict) -> Table:
    """
    Dynamically registers and creates a table based on a JSON schema definition.
    schema_def format:
    {
        "columns": [
            {"name": "id", "type": "INTEGER", "primary_key": true},
            {"name": "name", "type": "VARCHAR"}
        ],
        "composite_keys": ["id"]
    }
    """
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Clean table name
    table_name = table_name.lower().replace(".", "_").replace(" ", "_")
    
    if table_name in metadata.tables:
        print(f"[INFO] Table '{table_name}' already exists in database metadata.")
        return metadata.tables[table_name]
        
    columns = []
    
    # We will use composite_keys list if specified to mark columns as primary keys
    composite_keys = schema_def.get("composite_keys", [])
    
    for col_def in schema_def.get("columns", []):
        col_name = col_def["name"].lower().strip()
        col_type_str = col_def["type"]
        
        is_pk = col_def.get("primary_key", False) or col_name in composite_keys
        
        sa_type = map_type_string_to_sqlalchemy(col_type_str)
        columns.append(Column(col_name, sa_type, primary_key=is_pk))
        
    # If no primary keys are declared, add a standard autoincrement ID
    has_pk = any(col.primary_key for col in columns)
    if not has_pk:
        columns.insert(0, Column("id", Integer, primary_key=True, autoincrement=True))
        
    dynamic_table = Table(table_name, metadata, *columns)
    metadata.create_all(bind=engine)
    print(f"[SUCCESS] Dynamic table '{table_name}' created/verified.")
    return dynamic_table

def execute_differential_upsert(table_name: str, schema_def: dict, records: list[dict]) -> dict:
    """
    Executes a differential update/insert (UPSERT) based on matching composite/primary keys.
    Returns audit statistics.
    """
    if not records:
        return {"inserted": 0, "updated": 0, "failed": 0, "total": 0}
        
    table = get_or_create_dynamic_table(table_name, schema_def)
    inspector = inspect(engine)
    
    # Get primary/composite keys
    pk_columns = [col.name for col in table.columns if col.primary_key]
    
    # If no PK column, fallback to inspecting unique constraints or use first column
    if not pk_columns:
        pk_columns = [table.columns[0].name]
        
    print(f"[INFO] Performing differential upsert on '{table_name}' using keys: {pk_columns}")
    
    inserted = 0
    updated = 0
    failed = 0
    
    db = SessionLocal()
    try:
        for idx, rec in enumerate(records):
            # Clean record keys to lowercase
            clean_rec = {}
            for k, v in rec.items():
                clean_rec[k.lower().strip()] = v
                
            # Check if record exists
            where_clauses = []
            for pk in pk_columns:
                pk_val = clean_rec.get(pk)
                if pk_val is not None:
                    where_clauses.append(getattr(table.c, pk) == pk_val)
                    
            record_exists = False
            existing_row = None
            
            if where_clauses:
                query = select(table).where(*where_clauses)
                existing_row = db.execute(query).first()
                if existing_row:
                    record_exists = True
                    
            # Build insert/update dict with only valid column names
            valid_data = {}
            for col in table.columns:
                if col.name in clean_rec:
                    valid_data[col.name] = clean_rec[col.name]
                elif col.default is None and not col.primary_key and col.nullable:
                    # Keep nulls or default values
                    valid_data[col.name] = None
                    
            try:
                if record_exists:
                    # Compare and update if changed
                    # (To optimize, we can check if data matches exactly)
                    is_changed = False
                    for k, v in valid_data.items():
                        # Fetch the attribute value from the Row Proxy object
                        if hasattr(existing_row, k) and getattr(existing_row, k) != v:
                            is_changed = True
                            break
                        # Handle row mapping index access just in case
                        elif existing_row._mapping.get(k) != v:
                            is_changed = True
                            break
                            
                    if is_changed:
                        stmt = table.update().where(*where_clauses).values(**valid_data)
                        db.execute(stmt)
                        updated += 1
                else:
                    # Insert new record
                    stmt = table.insert().values(**valid_data)
                    db.execute(stmt)
                    inserted += 1
            except Exception as item_err:
                print(f"[WARNING] Failed to process record {idx}: {item_err}")
                failed += 1
                
        db.commit()
        print(f"[SUCCESS] Upsert complete. Inserted: {inserted}, Updated: {updated}, Failed: {failed}")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Differential upsert failed: {e}")
        failed = len(records)
    finally:
        db.close()
        
    return {
        "inserted": inserted,
        "updated": updated,
        "failed": failed,
        "total": len(records)
    }

# Flat File Output

def export_to_excel(records: list[dict], filename: str) -> str:
    """
    Generates a cleanly formatted Excel sheet from records.
    Ensures auto-adjusted column widths.
    """
    if not records:
        print("[WARNING] No records to export to Excel.")
        return ""
        
    os.makedirs(EXPORT_DIR, exist_ok=True)
    export_path = os.path.join(EXPORT_DIR, filename)
    
    # Use pandas to write to excel
    df = pd.DataFrame(records)
    
    # Excel Writer using openpyxl engine
    with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Extracted Data")
        
        # Format layout
        workbook = writer.book
        worksheet = writer.sheets["Extracted Data"]
        
        # Auto-fit columns
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    print(f"[SUCCESS] Data exported to formatted Excel workbook at: {export_path}")
    return export_path
