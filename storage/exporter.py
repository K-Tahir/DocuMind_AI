# storage/exporter.py
import os
import re
import pandas as pd
from sqlalchemy import create_engine

def export_tables_to_excel(tables: list, file_path: str) -> str:
    """
    Exports a list of extracted tables into an Excel file.
    Each table is written to its own sheet.
    """
    if not tables:
        print("[WARNING] No tables to export.")
        return ""
        
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for idx, table in enumerate(tables):
            data = table["data"]
            page = table["page"]
            table_idx = table["table_index"]
            
            if not data or len(data) < 1:
                continue
                
            # Use first row as columns, fallback if headers are duplicate or empty
            headers = data[0]
            rows = data[1:]
            
            clean_headers = []
            for i, h in enumerate(headers):
                h_str = str(h).strip() if h else f"Column_{i+1}"
                # Handle duplicates
                original_h = h_str
                counter = 1
                while h_str in clean_headers:
                    h_str = f"{original_h}_{counter}"
                    counter += 1
                clean_headers.append(h_str)
                
            # Create DataFrame
            df = pd.DataFrame(rows, columns=clean_headers)
            
            # Excel sheet name limit is 31 characters
            sheet_name = f"Page{page}_Table{table_idx}"[:30]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Format sheet columns for legibility
            worksheet = writer.sheets[sheet_name]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                
    print(f"[SUCCESS] Exported {len(tables)} tables to Excel workbook: {file_path}")
    return file_path

def export_tables_to_sql(tables: list, connection_url: str, base_table_name: str) -> dict:
    """
    Saves a list of extracted tables into a specified SQL Database.
    Replaces existing tables if they match the generated schema names.
    """
    if not tables:
        return {"status": "error", "message": "No tables to export."}
        
    try:
        engine = create_engine(connection_url)
        stats = {"inserted_tables": 0, "rows_inserted": 0}
        
        # Clean base table name
        safe_base_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_table_name.lower().strip())
        
        for idx, table in enumerate(tables):
            data = table["data"]
            page = table["page"]
            table_idx = table["table_index"]
            
            if not data or len(data) < 1:
                continue
                
            headers = data[0]
            rows = data[1:]
            
            # Clean column names to be SQL compliant
            clean_headers = []
            for i, h in enumerate(headers):
                h_str = re.sub(r'[^a-zA-Z0-9_]', '_', str(h).strip().lower()) if h else f"col_{i+1}"
                original_h = h_str
                counter = 1
                while h_str in clean_headers:
                    h_str = f"{original_h}_{counter}"
                    counter += 1
                clean_headers.append(h_str)
                
            df = pd.DataFrame(rows, columns=clean_headers)
            
            # Add metadata columns
            df["source_page"] = page
            df["extracted_table_index"] = table_idx
            
            table_name = f"{safe_base_name}_p{page}_t{table_idx}"
            
            # Dump to SQL table
            df.to_sql(table_name, con=engine, if_exists="replace", index=False)
            stats["inserted_tables"] += 1
            stats["rows_inserted"] += len(rows)
            
        print(f"[SUCCESS] Dynamic tables exported to SQL Database: {stats}")
        return {"status": "success", "stats": stats}
    except Exception as e:
        print(f"[ERROR] SQL Table Export failed: {e}")
        return {"status": "error", "message": str(e)}
