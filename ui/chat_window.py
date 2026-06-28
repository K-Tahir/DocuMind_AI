# Version: 1
# # ui/chat_window.py
# import os
# import threading
# import asyncio
# import subprocess
# import platform
# import customtkinter as ctk
# from tkinter import simpledialog, messagebox
# import config

# class ChatWindow(ctk.CTkFrame):
#     """
#     Main document interaction panel.
#     Renders the chat feed, quick-action buttons, and the message input area.
#     All heavy LLM / extraction work runs on background threads.
#     """

#     BG_COLOR        = "#0f1117"
#     CARD_COLOR      = "#1a1d27"
#     BORDER_COLOR    = "#2a2d3e"
#     ACCENT_BLUE     = "#4f8ef7"
#     ACCENT_PURPLE   = "#9d6ff7"
#     ACCENT_TEAL     = "#2dd4bf"
#     ACCENT_ORANGE   = "#fb923c"
#     TEXT_PRIMARY    = "#e8eaf6"
#     TEXT_SECONDARY  = "#7b7f9e"
#     SUCCESS_COLOR   = "#22c55e"
#     WARNING_COLOR   = "#f59e0b"
#     DANGER_COLOR    = "#ef4444"

#     # Bubble colours
#     USER_BUBBLE     = "#1e3a5f"
#     AI_BUBBLE       = "#1e1e2e"

#     def __init__(self, parent, api_key_provider, **kwargs):
#         super().__init__(parent, fg_color=self.BG_COLOR, corner_radius=0, **kwargs)

#         self._api_key_provider  = api_key_provider
#         self._session_id        = None
#         self._session_doc_name  = None
#         self._session_file_path = None
#         self._is_processing     = False

#         self.columnconfigure(0, weight=1)
#         self.rowconfigure(1, weight=1)

#         self._build_header()
#         self._build_chat_area()
#         self._build_quick_actions()
#         self._build_input_area()
#         self._show_welcome()

#     # ──────────────────────────────── Header ──────────────────────────────

#     def _build_header(self):
#         header = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=64)
#         header.grid(row=0, column=0, sticky="ew")
#         header.grid_propagate(False)
#         header.columnconfigure(1, weight=1)

#         self._doc_icon = ctk.CTkLabel(header, text="📄",
#                                       font=ctk.CTkFont(size=22))
#         self._doc_icon.grid(row=0, column=0, padx=(20, 8), pady=16)

#         self._doc_title = ctk.CTkLabel(
#             header,
#             text="No Document Selected — Upload a file to begin",
#             font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
#             text_color=self.TEXT_SECONDARY,
#             anchor="w"
#         )
#         self._doc_title.grid(row=0, column=1, sticky="w", pady=16)

#         self._status_pill = ctk.CTkLabel(
#             header, text="",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.SUCCESS_COLOR
#         )
#         self._status_pill.grid(row=0, column=2, padx=20, pady=16)

#     # ─────────────────────────────── Chat Area ────────────────────────────

#     def _build_chat_area(self):
#         self._chat_scroll = ctk.CTkScrollableFrame(
#             self, fg_color=self.BG_COLOR,
#             scrollbar_button_color=self.BORDER_COLOR,
#             scrollbar_button_hover_color=self.ACCENT_BLUE
#         )
#         self._chat_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
#         self._chat_scroll.columnconfigure(0, weight=1)
#         self._chat_row_index = 0

#     # ──────────────────────────── Quick Actions ───────────────────────────

#     def _build_quick_actions(self):
#         bar = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                            corner_radius=0, height=60)
#         bar.grid(row=2, column=0, sticky="ew")
#         bar.grid_propagate(False)

#         # Quick-action button definitions: (label, icon, accent, handler)
#         actions = [
#             ("Summarize",        "📝", self.ACCENT_BLUE,   self._action_summarize),
#             ("10 Bullet Points", "🔟", self.ACCENT_PURPLE, self._action_bullets),
#             ("Extract Tables",   "📊", self.ACCENT_TEAL,   self._action_extract_tables),
#             ("Extract Figures",  "🖼️",  self.ACCENT_ORANGE, self._action_extract_figures),
#             ("Agentic Ingest",   "🤖", "#a855f7",          self._action_agentic_ingest),
#         ]

#         inner = ctk.CTkFrame(bar, fg_color="transparent")
#         inner.pack(expand=True, fill="both", padx=12, pady=10)

#         for label, icon, color, cmd in actions:
#             ctk.CTkButton(
#                 inner,
#                 text=f"{icon}  {label}",
#                 height=36, corner_radius=10,
#                 fg_color=self.BORDER_COLOR,
#                 hover_color=color + "33",    # semi-transparent hover
#                 border_color=color,
#                 border_width=1,
#                 text_color=self.TEXT_PRIMARY,
#                 font=ctk.CTkFont(family="Segoe UI", size=12),
#                 command=cmd
#             ).pack(side="left", padx=(0, 8))

#     # ──────────────────────────── Input Area ──────────────────────────────

#     def _build_input_area(self):
#         footer = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=80)
#         footer.grid(row=3, column=0, sticky="ew")
#         footer.grid_propagate(False)
#         footer.columnconfigure(0, weight=1)

#         inner = ctk.CTkFrame(footer, fg_color="transparent")
#         inner.pack(expand=True, fill="both", padx=16, pady=14)
#         inner.columnconfigure(0, weight=1)

#         self._input_box = ctk.CTkEntry(
#             inner,
#             placeholder_text="Ask anything about your document… (e.g. What was on page 12?)",
#             height=44, corner_radius=12,
#             fg_color=self.BG_COLOR,
#             border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             placeholder_text_color=self.TEXT_SECONDARY,
#             font=ctk.CTkFont(family="Segoe UI", size=13)
#         )
#         self._input_box.grid(row=0, column=0, sticky="ew")
#         self._input_box.bind("<Return>", lambda e: self._send_message())

#         self._send_btn = ctk.CTkButton(
#             inner,
#             text="Send  ↑",
#             width=100, height=44, corner_radius=12,
#             fg_color=self.ACCENT_BLUE,
#             hover_color=self.ACCENT_PURPLE,
#             text_color="#ffffff",
#             font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#             command=self._send_message
#         )
#         self._send_btn.grid(row=0, column=1, padx=(10, 0))

#     # ──────────────────────────── Session Setup ───────────────────────────

#     def load_session(self, session_id: str, doc_name: str, file_path: str = None):
#         """Switches the chat view to a different session."""
#         self._session_id        = session_id
#         self._session_doc_name  = doc_name
#         self._session_file_path = file_path

#         self._doc_title.configure(text=doc_name, text_color=self.TEXT_PRIMARY)
#         self._status_pill.configure(text="● Ready", text_color=self.SUCCESS_COLOR)

#         # Clear chat and reload history
#         self._clear_chat()
#         self._load_history()

#     def _clear_chat(self):
#         for widget in self._chat_scroll.winfo_children():
#             widget.destroy()
#         self._chat_row_index = 0

#     def _load_history(self):
#         from storage.database import get_chat_history
#         history = get_chat_history(self._session_id)
#         for sender, message in history:
#             self._add_bubble(message, is_user=(sender == "user"), animate=False)

#     # ─────────────────────────── Chat Bubble ──────────────────────────────

#     def _add_bubble(self, text: str, is_user: bool, animate: bool = True):
#         """Renders a message bubble in the chat feed."""
#         outer = ctk.CTkFrame(self._chat_scroll, fg_color="transparent")
#         outer.grid(row=self._chat_row_index, column=0, sticky="ew",
#                    padx=12, pady=4)
#         outer.columnconfigure(0, weight=1)
#         self._chat_row_index += 1

#         bubble_color = self.USER_BUBBLE if is_user else self.AI_BUBBLE
#         anchor_side  = "e" if is_user else "w"
#         padx         = (120, 0) if is_user else (0, 120)

#         bubble = ctk.CTkFrame(outer, fg_color=bubble_color,
#                               corner_radius=14,
#                               border_color=self.ACCENT_BLUE if is_user else self.BORDER_COLOR,
#                               border_width=1)
#         bubble.pack(anchor=anchor_side, padx=padx)

#         # Sender label
#         sender_text = "You" if is_user else "🧠 DocuMind"
#         ctk.CTkLabel(bubble,
#                      text=sender_text,
#                      font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
#                      text_color=self.ACCENT_BLUE if is_user else self.ACCENT_PURPLE
#                      ).pack(anchor="w", padx=14, pady=(10, 2))

#         # Message text
#         msg_label = ctk.CTkLabel(bubble,
#                                  text=text,
#                                  font=ctk.CTkFont(family="Segoe UI", size=13),
#                                  text_color=self.TEXT_PRIMARY,
#                                  justify="left",
#                                  wraplength=520)
#         msg_label.pack(anchor="w", padx=14, pady=(0, 10))

#         # Auto-scroll to bottom
#         self._chat_scroll._parent_canvas.yview_moveto(1.0)
#         return msg_label

#     def _add_thinking_bubble(self) -> ctk.CTkLabel:
#         """Adds an animated thinking placeholder bubble."""
#         return self._add_bubble("⏳  Thinking…", is_user=False, animate=False)

#     def _show_welcome(self):
#         welcome = (
#             "👋  Welcome to DocuMind AI!\n\n"
#             "Upload a document using the sidebar to get started.\n\n"
#             "Once a document is loaded, you can:\n"
#             "  •  Ask questions about its content\n"
#             "  •  Request a summary or 10 bullet points\n"
#             "  •  Extract tables to Excel or a database\n"
#             "  •  Extract all figures/images to a folder\n"
#             "  •  Run full agentic data ingestion\n\n"
#             "All sessions and chat history are saved automatically."
#         )
#         self._add_bubble(welcome, is_user=False, animate=False)

#     # ─────────────────────────────── Send ─────────────────────────────────

#     def _send_message(self):
#         if self._is_processing:
#             return
#         query = self._input_box.get().strip()
#         if not query:
#             return
#         if not self._session_id:
#             messagebox.showwarning("No Document", "Please upload a document first.")
#             return

#         self._input_box.delete(0, "end")
#         self._add_bubble(query, is_user=True)
#         self._log_message("user", query)

#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._rag_query, thinking, query)

#     def _rag_query(self, query: str) -> str:
#         from core.rag_engine import query_document
#         return query_document(
#             session_id=self._session_id,
#             query=query,
#             api_key=self._api_key_provider()
#         )

#     # ─────────────────────────── Quick Actions ────────────────────────────

#     def _action_summarize(self):
#         if not self._guard():
#             return
#         prompt = (
#             "Please provide a concise yet comprehensive summary of this document. "
#             "Cover the main topic, key findings or arguments, and any important conclusions."
#         )
#         self._add_bubble("📝  Summarize this document", is_user=True)
#         self._log_message("user", "Summarize this document")
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._rag_query, thinking, prompt)

#     def _action_bullets(self):
#         if not self._guard():
#             return
#         prompt = (
#             "Extract exactly 10 key bullet points that capture the most important "
#             "information from this document. Format as a numbered list."
#         )
#         self._add_bubble("🔟  Give me 10 bullet-point summary", is_user=True)
#         self._log_message("user", "10 bullet-point summary")
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._rag_query, thinking, prompt)

#     def _action_extract_tables(self):
#         if not self._guard():
#             return
#         if not self._session_file_path:
#             messagebox.showwarning("No File Path",
#                                    "The original file path is not stored for this session.")
#             return

#         # Ask export format
#         choice = simpledialog.askstring(
#             "Export Format",
#             "Where do you want to save the extracted tables?\n\n"
#             "Type  excel  for an Excel workbook (.xlsx)\n"
#             "Type  sql    to save to the database\n",
#             initialvalue="excel"
#         )
#         if not choice:
#             return
#         choice = choice.strip().lower()
#         if choice not in ("excel", "sql"):
#             messagebox.showwarning("Invalid Choice", "Please enter 'excel' or 'sql'.")
#             return

#         self._add_bubble(f"📊  Extracting all tables → {choice.upper()} format…", is_user=True)
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._do_extract_tables, thinking, choice)

#     def _do_extract_tables(self, export_format: str) -> str:
#         from core.parser import (extract_pdf_tables, extract_docx_tables)
#         from storage.exporter import export_tables_to_excel, export_tables_to_sql

#         ext = os.path.splitext(self._session_file_path)[1].lower()
#         if ext == ".pdf":
#             tables = extract_pdf_tables(self._session_file_path)
#         elif ext == ".docx":
#             tables = extract_docx_tables(self._session_file_path)
#         else:
#             return "⚠️  Table extraction is supported for PDF and DOCX files only."

#         if not tables:
#             return "ℹ️  No tables were detected in this document."

#         base_name = os.path.splitext(os.path.basename(self._session_file_path))[0]
#         export_dir = str(config.EXPORT_DIR)
#         os.makedirs(export_dir, exist_ok=True)

#         if export_format == "excel":
#             out_path = os.path.join(export_dir, f"{base_name}_tables.xlsx")
#             export_tables_to_excel(tables, out_path)
#             return (
#                 f"✅  Extracted {len(tables)} table(s) successfully!\n\n"
#                 f"📁  Saved to:\n{out_path}\n\n"
#                 f"Click the folder button below to open the directory."
#             )
#         else:  # sql
#             db_url = config.DATABASE_URL
#             result = export_tables_to_sql(tables, db_url, base_name)
#             if result["status"] == "success":
#                 s = result["stats"]
#                 return (
#                     f"✅  Exported {s['inserted_tables']} table(s) → {s['rows_inserted']} rows "
#                     f"to the database successfully!\n\n"
#                     f"Database: {db_url}"
#                 )
#             else:
#                 return f"❌  SQL export failed: {result.get('message', 'Unknown error')}"

#     def _action_extract_figures(self):
#         if not self._guard():
#             return
#         if not self._session_file_path:
#             messagebox.showwarning("No File Path",
#                                    "The original file path is not stored for this session.")
#             return

#         self._add_bubble("🖼️  Extracting all figures from the document…", is_user=True)
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._do_extract_figures, thinking)

#     def _do_extract_figures(self) -> str:
#         from core.parser import (extract_pdf_images, extract_docx_images)

#         base_name = os.path.splitext(os.path.basename(self._session_file_path))[0]
#         output_dir = os.path.join(str(config.EXPORT_DIR), "figures",
#                                   self._session_id[:8])
#         os.makedirs(output_dir, exist_ok=True)

#         ext = os.path.splitext(self._session_file_path)[1].lower()
#         if ext == ".pdf":
#             images = extract_pdf_images(self._session_file_path, output_dir)
#         elif ext == ".docx":
#             images = extract_docx_images(self._session_file_path, output_dir)
#         else:
#             return "⚠️  Figure extraction is supported for PDF and DOCX files only."

#         if not images:
#             return "ℹ️  No embedded images/figures were detected in this document."

#         return (
#             f"✅  Extracted {len(images)} figure(s) successfully!\n\n"
#             f"📁  Saved to:\n{output_dir}"
#         )

#     def _action_agentic_ingest(self):
#         if not self._guard():
#             return
#         if not self._session_file_path:
#             messagebox.showwarning("No File Path",
#                                    "The original file path is not stored for this session.")
#             return

#         confirm = messagebox.askyesno(
#             "Agentic Ingest",
#             "This will run the full LangGraph pipeline:\n\n"
#             "  1. Parse and analyze the document structure\n"
#             "  2. Discover a database schema via Gemini AI\n"
#             "  3. Extract all structured records\n"
#             "  4. Validate and self-heal data errors\n"
#             "  5. Upsert records to your database\n"
#             "  6. Export an Excel workbook\n\n"
#             "This may take 30–90 seconds. Continue?"
#         )
#         if not confirm:
#             return

#         self._add_bubble("🤖  Running Agentic Ingestion Pipeline…", is_user=True)
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._do_agentic_ingest, thinking)

#     def _do_agentic_ingest(self) -> str:
#         """Runs the LangGraph pipeline synchronously in a background thread."""
#         import asyncio
#         from core.agent_flow import build_agent_graph

#         graph = build_agent_graph()
#         file_ext = os.path.splitext(self._session_file_path)[1].replace(".", "").lower()
#         initial_state = {
#             "file_path": self._session_file_path,
#             "file_type": file_ext,
#             "retry_count": 0
#         }

#         try:
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             result = loop.run_until_complete(graph.ainvoke(initial_state))
#             loop.close()
#         except Exception as e:
#             return f"❌  Agentic pipeline failed:\n{str(e)}"

#         status      = result.get("status", "UNKNOWN")
#         schema      = result.get("schema_name", "N/A")
#         n_records   = len(result.get("extracted_data", []))
#         db_stats    = result.get("database_upsert_stats", {})
#         excel_path  = result.get("export_path", "N/A")
#         errors      = result.get("validation_errors", [])
#         retries     = result.get("retry_count", 0)

#         lines = [
#             f"✅  Agentic Ingestion Complete!\n",
#             f"📊  Status:      {status}",
#             f"🗄️   Schema:      {schema}",
#             f"📋  Records:     {n_records} extracted",
#             f"💾  DB Inserted: {db_stats.get('inserted', 0)} / Updated: {db_stats.get('updated', 0)}",
#             f"🔁  Self-Heals:  {retries} retries",
#             f"📁  Excel:       {excel_path}",
#         ]
#         if errors:
#             lines.append(f"\n⚠️  Validation issues: {len(errors)}")
#             for e in errors[:3]:
#                 lines.append(f"   • {e}")
#             if len(errors) > 3:
#                 lines.append(f"   … and {len(errors) - 3} more")

#         return "\n".join(lines)

#     # ────────────────────────────── Threading ─────────────────────────────

#     def _run_in_thread(self, task_fn, thinking_label: ctk.CTkLabel, *args):
#         """
#         Executes task_fn(*args) in a daemon thread.
#         Replaces the thinking_label text with the result on the main thread.
#         """
#         self._set_busy(True)

#         def worker():
#             try:
#                 result = task_fn(*args)
#             except Exception as e:
#                 import traceback
#                 traceback.print_exc()
#                 result = f"❌  An error occurred:\n{str(e)}"
#             self.after(0, self._finish_response, thinking_label, result)

#         threading.Thread(target=worker, daemon=True).start()

#     def _finish_response(self, thinking_label: ctk.CTkLabel, text: str):
#         thinking_label.configure(text=text)
#         self._log_message("ai", text)
#         self._set_busy(False)
#         self._chat_scroll._parent_canvas.yview_moveto(1.0)

#     def _set_busy(self, busy: bool):
#         self._is_processing = busy
#         state = "disabled" if busy else "normal"
#         self._send_btn.configure(state=state)
#         self._input_box.configure(state=state)

#     # ────────────────────────────── Helpers ───────────────────────────────

#     def _guard(self) -> bool:
#         """Returns False and shows a warning if no session is active."""
#         if not self._session_id:
#             messagebox.showwarning("No Document",
#                                    "Please upload a document first.")
#             return False
#         if self._is_processing:
#             messagebox.showinfo("Processing", "Please wait for the current task to complete.")
#             return False
#         return True

#     def _log_message(self, sender: str, message: str):
#         if self._session_id:
#             from storage.database import log_message
#             log_message(self._session_id, sender, message)

#     @staticmethod
#     def _open_folder(path: str):
#         """Opens a directory in the native file explorer."""
#         if platform.system() == "Windows":
#             os.startfile(path)
#         elif platform.system() == "Darwin":
#             subprocess.Popen(["open", path])
#         else:
#             subprocess.Popen(["xdg-open", path])

# Version: 2

# # ui/chat_window.py
# import os
# import threading
# import asyncio
# import subprocess
# import platform
# import customtkinter as ctk
# from tkinter import simpledialog, messagebox
# import config


# class ChatWindow(ctk.CTkFrame):
#     """
#     Main document interaction panel.
#     Renders the chat feed, quick-action buttons, and the message input area.
#     All heavy LLM / extraction work runs on background threads.

#     API keys are always read LIVE from config at the moment of each call —
#     never captured at construction time — so keys set via Settings take
#     effect immediately without restarting the app.
#     """

#     BG_COLOR       = "#0f1117"
#     CARD_COLOR     = "#1a1d27"
#     BORDER_COLOR   = "#2a2d3e"
#     ACCENT_BLUE    = "#4f8ef7"
#     ACCENT_PURPLE  = "#9d6ff7"
#     ACCENT_TEAL    = "#2dd4bf"
#     ACCENT_ORANGE  = "#fb923c"
#     TEXT_PRIMARY   = "#e8eaf6"
#     TEXT_SECONDARY = "#7b7f9e"
#     SUCCESS_COLOR  = "#22c55e"
#     WARNING_COLOR  = "#f59e0b"
#     DANGER_COLOR   = "#ef4444"

#     USER_BUBBLE    = "#1e3a5f"
#     AI_BUBBLE      = "#1e1e2e"

#     def __init__(self, parent, api_key_provider=None, **kwargs):
#         # api_key_provider kept in signature for backward compat with main.py
#         # but is intentionally NOT used anywhere — config is always read live
#         super().__init__(parent, fg_color=self.BG_COLOR, corner_radius=0, **kwargs)

#         self._session_id        = None
#         self._session_doc_name  = None
#         self._session_file_path = None
#         self._is_processing     = False

#         self.columnconfigure(0, weight=1)
#         self.rowconfigure(1, weight=1)

#         self._build_header()
#         self._build_chat_area()
#         self._build_quick_actions()
#         self._build_input_area()
#         self._show_welcome()

#     # ──────────────────────────────── Header ──────────────────────────────

#     def _build_header(self):
#         header = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=64)
#         header.grid(row=0, column=0, sticky="ew")
#         header.grid_propagate(False)
#         header.columnconfigure(1, weight=1)

#         self._doc_icon = ctk.CTkLabel(header, text="📄",
#                                       font=ctk.CTkFont(size=22))
#         self._doc_icon.grid(row=0, column=0, padx=(20, 8), pady=16)

#         self._doc_title = ctk.CTkLabel(
#             header,
#             text="No Document Selected — Upload a file to begin",
#             font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
#             text_color=self.TEXT_SECONDARY,
#             anchor="w"
#         )
#         self._doc_title.grid(row=0, column=1, sticky="w", pady=16)

#         self._status_pill = ctk.CTkLabel(
#             header, text="",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.SUCCESS_COLOR
#         )
#         self._status_pill.grid(row=0, column=2, padx=20, pady=16)

#     # ─────────────────────────────── Chat Area ────────────────────────────

#     def _build_chat_area(self):
#         self._chat_scroll = ctk.CTkScrollableFrame(
#             self, fg_color=self.BG_COLOR,
#             scrollbar_button_color=self.BORDER_COLOR,
#             scrollbar_button_hover_color=self.ACCENT_BLUE
#         )
#         self._chat_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
#         self._chat_scroll.columnconfigure(0, weight=1)
#         self._chat_row_index = 0

#     # ──────────────────────────── Quick Actions ───────────────────────────

#     def _build_quick_actions(self):
#         bar = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                            corner_radius=0, height=60)
#         bar.grid(row=2, column=0, sticky="ew")
#         bar.grid_propagate(False)

#         actions = [
#             ("Summarize",        "📝", self.ACCENT_BLUE,   self._action_summarize),
#             ("10 Bullet Points", "🔟", self.ACCENT_PURPLE, self._action_bullets),
#             ("Extract Tables",   "📊", self.ACCENT_TEAL,   self._action_extract_tables),
#             ("Extract Figures",  "🖼️",  self.ACCENT_ORANGE, self._action_extract_figures),
#             ("Agentic Ingest",   "🤖", "#a855f7",          self._action_agentic_ingest),
#         ]

#         inner = ctk.CTkFrame(bar, fg_color="transparent")
#         inner.pack(expand=True, fill="both", padx=12, pady=10)

#         for label, icon, color, cmd in actions:
#             ctk.CTkButton(
#                 inner,
#                 text=f"{icon}  {label}",
#                 height=36, corner_radius=10,
#                 fg_color=self.BORDER_COLOR,
#                 hover_color=color + "33",
#                 border_color=color,
#                 border_width=1,
#                 text_color=self.TEXT_PRIMARY,
#                 font=ctk.CTkFont(family="Segoe UI", size=12),
#                 command=cmd
#             ).pack(side="left", padx=(0, 8))

#     # ──────────────────────────── Input Area ──────────────────────────────

#     def _build_input_area(self):
#         footer = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=80)
#         footer.grid(row=3, column=0, sticky="ew")
#         footer.grid_propagate(False)
#         footer.columnconfigure(0, weight=1)

#         inner = ctk.CTkFrame(footer, fg_color="transparent")
#         inner.pack(expand=True, fill="both", padx=16, pady=14)
#         inner.columnconfigure(0, weight=1)

#         self._input_box = ctk.CTkEntry(
#             inner,
#             placeholder_text="Ask anything about your document… (e.g. What was on page 12?)",
#             height=44, corner_radius=12,
#             fg_color=self.BG_COLOR,
#             border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             placeholder_text_color=self.TEXT_SECONDARY,
#             font=ctk.CTkFont(family="Segoe UI", size=13)
#         )
#         self._input_box.grid(row=0, column=0, sticky="ew")
#         self._input_box.bind("<Return>", lambda e: self._send_message())

#         self._send_btn = ctk.CTkButton(
#             inner,
#             text="Send  ↑",
#             width=100, height=44, corner_radius=12,
#             fg_color=self.ACCENT_BLUE,
#             hover_color=self.ACCENT_PURPLE,
#             text_color="#ffffff",
#             font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#             command=self._send_message
#         )
#         self._send_btn.grid(row=0, column=1, padx=(10, 0))

#     # ──────────────────────────── Session Setup ───────────────────────────

#     def load_session(self, session_id: str, doc_name: str, file_path: str = None):
#         self._session_id        = session_id
#         self._session_doc_name  = doc_name
#         self._session_file_path = file_path

#         self._doc_title.configure(text=doc_name, text_color=self.TEXT_PRIMARY)
#         self._status_pill.configure(text="● Ready", text_color=self.SUCCESS_COLOR)

#         self._clear_chat()
#         self._load_history()

#     def _clear_chat(self):
#         for widget in self._chat_scroll.winfo_children():
#             widget.destroy()
#         self._chat_row_index = 0

#     def _load_history(self):
#         from storage.database import get_chat_history
#         history = get_chat_history(self._session_id)
#         for sender, message in history:
#             self._add_bubble(message, is_user=(sender == "user"), animate=False)

#     # ─────────────────────────── Chat Bubble ──────────────────────────────

#     def _add_bubble(self, text: str, is_user: bool, animate: bool = True):
#         outer = ctk.CTkFrame(self._chat_scroll, fg_color="transparent")
#         outer.grid(row=self._chat_row_index, column=0, sticky="ew",
#                    padx=12, pady=4)
#         outer.columnconfigure(0, weight=1)
#         self._chat_row_index += 1

#         bubble_color = self.USER_BUBBLE if is_user else self.AI_BUBBLE
#         anchor_side  = "e" if is_user else "w"
#         padx         = (120, 0) if is_user else (0, 120)

#         bubble = ctk.CTkFrame(outer, fg_color=bubble_color,
#                               corner_radius=14,
#                               border_color=self.ACCENT_BLUE if is_user else self.BORDER_COLOR,
#                               border_width=1)
#         bubble.pack(anchor=anchor_side, padx=padx)

#         sender_text = "You" if is_user else "🧠 DocuMind"
#         ctk.CTkLabel(bubble,
#                      text=sender_text,
#                      font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
#                      text_color=self.ACCENT_BLUE if is_user else self.ACCENT_PURPLE
#                      ).pack(anchor="w", padx=14, pady=(10, 2))

#         msg_label = ctk.CTkLabel(bubble,
#                                  text=text,
#                                  font=ctk.CTkFont(family="Segoe UI", size=13),
#                                  text_color=self.TEXT_PRIMARY,
#                                  justify="left",
#                                  wraplength=520)
#         msg_label.pack(anchor="w", padx=14, pady=(0, 10))

#         self._chat_scroll._parent_canvas.yview_moveto(1.0)
#         return msg_label

#     def _add_thinking_bubble(self) -> ctk.CTkLabel:
#         return self._add_bubble("⏳  Thinking…", is_user=False, animate=False)

#     def _show_welcome(self):
#         welcome = (
#             "👋  Welcome to DocuMind AI!\n\n"
#             "Upload a document using the sidebar to get started.\n\n"
#             "Once a document is loaded, you can:\n"
#             "  •  Ask questions about its content\n"
#             "  •  Request a summary or 10 bullet points\n"
#             "  •  Extract tables to Excel or a database\n"
#             "  •  Extract all figures/images to a folder\n"
#             "  •  Run full agentic data ingestion\n\n"
#             "All sessions and chat history are saved automatically."
#         )
#         self._add_bubble(welcome, is_user=False, animate=False)

#     # ─────────────────────────────── Send ─────────────────────────────────

#     def _send_message(self):
#         if self._is_processing:
#             return
#         query = self._input_box.get().strip()
#         if not query:
#             return
#         if not self._session_id:
#             messagebox.showwarning("No Document", "Please upload a document first.")
#             return

#         # ── Guard: warn user if no API key is set before even trying ─────
#         if config.ACTIVE_PROVIDER != "Ollama" and not config.get_active_api_key():
#             messagebox.showwarning(
#                 "API Key Missing",
#                 f"No {config.ACTIVE_PROVIDER} API key is set.\n\n"
#                 "Go to ⚙ Settings, paste your API key, and click ⚡ Apply Now.\n"
#                 "Then try again — no restart needed."
#             )
#             return

#         self._input_box.delete(0, "end")
#         self._add_bubble(query, is_user=True)
#         self._log_message("user", query)

#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._rag_query, thinking, query)

#     def _rag_query(self, query: str) -> str:
#         """
#         Calls query_document with NO api_key argument.
#         rag_engine.py reads the live key from config internally.
#         """
#         from core.rag_engine import query_document
#         return query_document(
#             session_id=self._session_id,
#             query=query
#             # api_key intentionally omitted — rag_engine reads config directly
#         )

#     # ─────────────────────────── Quick Actions ────────────────────────────

#     def _action_summarize(self):
#         if not self._guard():
#             return
#         prompt = (
#             "Please provide a concise yet comprehensive summary of this document. "
#             "Cover the main topic, key findings or arguments, and any important conclusions."
#         )
#         self._add_bubble("📝  Summarize this document", is_user=True)
#         self._log_message("user", "Summarize this document")
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._rag_query, thinking, prompt)

#     def _action_bullets(self):
#         if not self._guard():
#             return
#         prompt = (
#             "Extract exactly 10 key bullet points that capture the most important "
#             "information from this document. Format as a numbered list."
#         )
#         self._add_bubble("🔟  Give me 10 bullet-point summary", is_user=True)
#         self._log_message("user", "10 bullet-point summary")
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._rag_query, thinking, prompt)

#     def _action_extract_tables(self):
#         if not self._guard():
#             return
#         if not self._session_file_path:
#             messagebox.showwarning("No File Path",
#                                    "The original file path is not stored for this session.")
#             return

#         choice = simpledialog.askstring(
#             "Export Format",
#             "Where do you want to save the extracted tables?\n\n"
#             "Type  excel  for an Excel workbook (.xlsx)\n"
#             "Type  sql    to save to the database\n",
#             initialvalue="excel"
#         )
#         if not choice:
#             return
#         choice = choice.strip().lower()
#         if choice not in ("excel", "sql"):
#             messagebox.showwarning("Invalid Choice", "Please enter 'excel' or 'sql'.")
#             return

#         self._add_bubble(f"📊  Extracting all tables → {choice.upper()} format…", is_user=True)
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._do_extract_tables, thinking, choice)

#     def _do_extract_tables(self, export_format: str) -> str:
#         from core.parser import extract_pdf_tables, extract_docx_tables
#         from storage.exporter import export_tables_to_excel, export_tables_to_sql

#         ext = os.path.splitext(self._session_file_path)[1].lower()
#         if ext == ".pdf":
#             tables = extract_pdf_tables(self._session_file_path)
#         elif ext == ".docx":
#             tables = extract_docx_tables(self._session_file_path)
#         else:
#             return "⚠️  Table extraction is supported for PDF and DOCX files only."

#         if not tables:
#             return "ℹ️  No tables were detected in this document."

#         base_name  = os.path.splitext(os.path.basename(self._session_file_path))[0]
#         export_dir = str(config.EXPORT_DIR)
#         os.makedirs(export_dir, exist_ok=True)

#         if export_format == "excel":
#             out_path = os.path.join(export_dir, f"{base_name}_tables.xlsx")
#             export_tables_to_excel(tables, out_path)
#             return (
#                 f"✅  Extracted {len(tables)} table(s) successfully!\n\n"
#                 f"📁  Saved to:\n{out_path}\n\n"
#                 f"Click the folder button below to open the directory."
#             )
#         else:
#             db_url = config.DATABASE_URL
#             result = export_tables_to_sql(tables, db_url, base_name)
#             if result["status"] == "success":
#                 s = result["stats"]
#                 return (
#                     f"✅  Exported {s['inserted_tables']} table(s) → "
#                     f"{s['rows_inserted']} rows to the database successfully!\n\n"
#                     f"Database: {db_url}"
#                 )
#             else:
#                 return f"❌  SQL export failed: {result.get('message', 'Unknown error')}"

#     def _action_extract_figures(self):
#         if not self._guard():
#             return
#         if not self._session_file_path:
#             messagebox.showwarning("No File Path",
#                                    "The original file path is not stored for this session.")
#             return

#         self._add_bubble("🖼️  Extracting all figures from the document…", is_user=True)
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._do_extract_figures, thinking)

#     def _do_extract_figures(self) -> str:
#         from core.parser import extract_pdf_images, extract_docx_images

#         base_name  = os.path.splitext(os.path.basename(self._session_file_path))[0]
#         output_dir = os.path.join(str(config.EXPORT_DIR), "figures",
#                                   self._session_id[:8])
#         os.makedirs(output_dir, exist_ok=True)

#         ext = os.path.splitext(self._session_file_path)[1].lower()
#         if ext == ".pdf":
#             images = extract_pdf_images(self._session_file_path, output_dir)
#         elif ext == ".docx":
#             images = extract_docx_images(self._session_file_path, output_dir)
#         else:
#             return "⚠️  Figure extraction is supported for PDF and DOCX files only."

#         if not images:
#             return "ℹ️  No embedded images/figures were detected in this document."

#         return (
#             f"✅  Extracted {len(images)} figure(s) successfully!\n\n"
#             f"📁  Saved to:\n{output_dir}"
#         )

#     def _action_agentic_ingest(self):
#         if not self._guard():
#             return
#         if not self._session_file_path:
#             messagebox.showwarning("No File Path",
#                                    "The original file path is not stored for this session.")
#             return

#         confirm = messagebox.askyesno(
#             "Agentic Ingest",
#             "This will run the full LangGraph pipeline:\n\n"
#             "  1. Parse and analyze the document structure\n"
#             "  2. Discover a database schema via AI\n"
#             "  3. Extract all structured records\n"
#             "  4. Validate and self-heal data errors\n"
#             "  5. Upsert records to your database\n"
#             "  6. Export an Excel workbook\n\n"
#             "This may take 30–90 seconds. Continue?"
#         )
#         if not confirm:
#             return

#         self._add_bubble("🤖  Running Agentic Ingestion Pipeline…", is_user=True)
#         thinking = self._add_thinking_bubble()
#         self._run_in_thread(self._do_agentic_ingest, thinking)

#     def _do_agentic_ingest(self) -> str:
#         from core.agent_flow import build_agent_graph

#         graph    = build_agent_graph()
#         file_ext = os.path.splitext(self._session_file_path)[1].replace(".", "").lower()
#         initial_state = {
#             "file_path"  : self._session_file_path,
#             "file_type"  : file_ext,
#             "retry_count": 0
#         }

#         try:
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             result = loop.run_until_complete(graph.ainvoke(initial_state))
#             loop.close()
#         except Exception as e:
#             return f"❌  Agentic pipeline failed:\n{str(e)}"

#         status    = result.get("status", "UNKNOWN")
#         schema    = result.get("schema_name", "N/A")
#         n_records = len(result.get("extracted_data", []))
#         db_stats  = result.get("database_upsert_stats", {})
#         excel     = result.get("export_path", "N/A")
#         errors    = result.get("validation_errors", [])
#         retries   = result.get("retry_count", 0)

#         lines = [
#             f"✅  Agentic Ingestion Complete!\n",
#             f"📊  Status:      {status}",
#             f"🗄️   Schema:      {schema}",
#             f"📋  Records:     {n_records} extracted",
#             f"💾  DB Inserted: {db_stats.get('inserted', 0)} / Updated: {db_stats.get('updated', 0)}",
#             f"🔁  Self-Heals:  {retries} retries",
#             f"📁  Excel:       {excel}",
#         ]
#         if errors:
#             lines.append(f"\n⚠️  Validation issues: {len(errors)}")
#             for e in errors[:3]:
#                 lines.append(f"   • {e}")
#             if len(errors) > 3:
#                 lines.append(f"   … and {len(errors) - 3} more")

#         return "\n".join(lines)

#     # ────────────────────────────── Threading ─────────────────────────────

#     def _run_in_thread(self, task_fn, thinking_label: ctk.CTkLabel, *args):
#         self._set_busy(True)

#         def worker():
#             try:
#                 result = task_fn(*args)
#             except Exception as e:
#                 import traceback
#                 traceback.print_exc()
#                 result = f"❌  An error occurred:\n{str(e)}"
#             self.after(0, self._finish_response, thinking_label, result)

#         threading.Thread(target=worker, daemon=True).start()

#     def _finish_response(self, thinking_label: ctk.CTkLabel, text: str):
#         thinking_label.configure(text=text)
#         self._log_message("ai", text)
#         self._set_busy(False)
#         self._chat_scroll._parent_canvas.yview_moveto(1.0)

#     def _set_busy(self, busy: bool):
#         self._is_processing = busy
#         state = "disabled" if busy else "normal"
#         self._send_btn.configure(state=state)
#         self._input_box.configure(state=state)

#     # ────────────────────────────── Helpers ───────────────────────────────

#     def _guard(self) -> bool:
#         if not self._session_id:
#             messagebox.showwarning("No Document", "Please upload a document first.")
#             return False
#         if self._is_processing:
#             messagebox.showinfo("Processing",
#                                 "Please wait for the current task to complete.")
#             return False
#         return True

#     def _log_message(self, sender: str, message: str):
#         if self._session_id:
#             from storage.database import log_message
#             log_message(self._session_id, sender, message)

#     @staticmethod
#     def _open_folder(path: str):
#         if platform.system() == "Windows":
#             os.startfile(path)
#         elif platform.system() == "Darwin":
#             subprocess.Popen(["open", path])
#         else:
#             subprocess.Popen(["xdg-open", path])

# Version: 3

# ui/chat_window.py
import os
import threading
import asyncio
import subprocess
import platform
import customtkinter as ctk
from tkinter import simpledialog, messagebox
import config


class ChatWindow(ctk.CTkFrame):
    """
    Main document interaction panel.
    Renders the chat feed, quick-action buttons, and the message input area.
    All heavy LLM / extraction work runs on background threads.

    API keys are always read LIVE from config at the moment of each call —
    never captured at construction time — so keys set via Settings take
    effect immediately without restarting the app.
    """

    BG_COLOR       = "#0f1117"
    CARD_COLOR     = "#1a1d27"
    BORDER_COLOR   = "#2a2d3e"
    ACCENT_BLUE    = "#4f8ef7"
    ACCENT_PURPLE  = "#9d6ff7"
    ACCENT_TEAL    = "#2dd4bf"
    ACCENT_ORANGE  = "#fb923c"
    TEXT_PRIMARY   = "#e8eaf6"
    TEXT_SECONDARY = "#7b7f9e"
    SUCCESS_COLOR  = "#22c55e"
    WARNING_COLOR  = "#f59e0b"
    DANGER_COLOR   = "#ef4444"

    USER_BUBBLE    = "#1e3a5f"
    AI_BUBBLE      = "#1e1e2e"

    def __init__(self, parent, api_key_provider=None, **kwargs):
        # api_key_provider kept in signature for backward compat with main.py
        # but is intentionally NOT used anywhere — config is always read live
        super().__init__(parent, fg_color=self.BG_COLOR, corner_radius=0, **kwargs)

        self._session_id        = None
        self._session_doc_name  = None
        self._session_file_path = None
        self._is_processing     = False

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_chat_area()
        self._build_quick_actions()
        self._build_input_area()
        self._show_welcome()

    # ──────────────────────────────── Header ──────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
                              corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(1, weight=1)

        self._doc_icon = ctk.CTkLabel(header, text="📄",
                                      font=ctk.CTkFont(size=22))
        self._doc_icon.grid(row=0, column=0, padx=(20, 8), pady=16)

        self._doc_title = ctk.CTkLabel(
            header,
            text="No Document Selected — Upload a file to begin",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=self.TEXT_SECONDARY,
            anchor="w"
        )
        self._doc_title.grid(row=0, column=1, sticky="w", pady=16)

        self._status_pill = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.SUCCESS_COLOR
        )
        self._status_pill.grid(row=0, column=2, padx=20, pady=16)

    # ─────────────────────────────── Chat Area ────────────────────────────

    def _build_chat_area(self):
        self._chat_scroll = ctk.CTkScrollableFrame(
            self, fg_color=self.BG_COLOR,
            scrollbar_button_color=self.BORDER_COLOR,
            scrollbar_button_hover_color=self.ACCENT_BLUE
        )
        self._chat_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._chat_scroll.columnconfigure(0, weight=1)
        self._chat_row_index = 0

    # ──────────────────────────── Quick Actions ───────────────────────────

    def _build_quick_actions(self):
        bar = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
                           corner_radius=0, height=60)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)

        # (label, icon, border_color, hover_color, handler)
        # hover_color must be valid 6-digit hex — Tkinter rejects 8-digit RGBA
        actions = [
            ("Summarize",        "📝", self.ACCENT_BLUE,   "#1e3a6e", self._action_summarize),
            ("10 Bullet Points", "🔟", self.ACCENT_PURPLE, "#2e1e5e", self._action_bullets),
            ("Extract Tables",   "📊", self.ACCENT_TEAL,   "#1a3a38", self._action_extract_tables),
            ("Extract Figures",  "🖼️",  self.ACCENT_ORANGE, "#3e2a1e", self._action_extract_figures),
            ("Agentic Ingest",   "🤖", "#a855f7",          "#2e1a4e", self._action_agentic_ingest),
        ]

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=12, pady=10)

        for label, icon, border_color, hover_color, cmd in actions:
            ctk.CTkButton(
                inner,
                text=f"{icon}  {label}",
                height=36, corner_radius=10,
                fg_color=self.BORDER_COLOR,
                hover_color=hover_color,
                border_color=border_color,
                border_width=1,
                text_color=self.TEXT_PRIMARY,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                command=cmd
            ).pack(side="left", padx=(0, 8))

    # ──────────────────────────── Input Area ──────────────────────────────

    def _build_input_area(self):
        footer = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
                              corner_radius=0, height=80)
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(footer, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=16, pady=14)
        inner.columnconfigure(0, weight=1)

        self._input_box = ctk.CTkEntry(
            inner,
            placeholder_text="Ask anything about your document… (e.g. What was on page 12?)",
            height=44, corner_radius=12,
            fg_color=self.BG_COLOR,
            border_color=self.BORDER_COLOR,
            text_color=self.TEXT_PRIMARY,
            placeholder_text_color=self.TEXT_SECONDARY,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self._input_box.grid(row=0, column=0, sticky="ew")
        self._input_box.bind("<Return>", lambda e: self._send_message())

        self._send_btn = ctk.CTkButton(
            inner,
            text="Send  ↑",
            width=100, height=44, corner_radius=12,
            fg_color=self.ACCENT_BLUE,
            hover_color=self.ACCENT_PURPLE,
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._send_message
        )
        self._send_btn.grid(row=0, column=1, padx=(10, 0))

    # ──────────────────────────── Session Setup ───────────────────────────

    def load_session(self, session_id: str, doc_name: str, file_path: str = None):
        self._session_id        = session_id
        self._session_doc_name  = doc_name
        self._session_file_path = file_path

        self._doc_title.configure(text=doc_name, text_color=self.TEXT_PRIMARY)
        self._status_pill.configure(text="● Ready", text_color=self.SUCCESS_COLOR)

        self._clear_chat()
        self._load_history()

    def _clear_chat(self):
        for widget in self._chat_scroll.winfo_children():
            widget.destroy()
        self._chat_row_index = 0

    def _load_history(self):
        from storage.database import get_chat_history
        history = get_chat_history(self._session_id)
        for sender, message in history:
            self._add_bubble(message, is_user=(sender == "user"), animate=False)

    # ─────────────────────────── Chat Bubble ──────────────────────────────

    def _add_bubble(self, text: str, is_user: bool, animate: bool = True):
        outer = ctk.CTkFrame(self._chat_scroll, fg_color="transparent")
        outer.grid(row=self._chat_row_index, column=0, sticky="ew",
                   padx=12, pady=4)
        outer.columnconfigure(0, weight=1)
        self._chat_row_index += 1

        bubble_color = self.USER_BUBBLE if is_user else self.AI_BUBBLE
        anchor_side  = "e" if is_user else "w"
        padx         = (120, 0) if is_user else (0, 120)

        bubble = ctk.CTkFrame(outer, fg_color=bubble_color,
                              corner_radius=14,
                              border_color=self.ACCENT_BLUE if is_user else self.BORDER_COLOR,
                              border_width=1)
        bubble.pack(anchor=anchor_side, padx=padx)

        sender_text = "You" if is_user else "🧠 DocuMind"
        ctk.CTkLabel(bubble,
                     text=sender_text,
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.ACCENT_BLUE if is_user else self.ACCENT_PURPLE
                     ).pack(anchor="w", padx=14, pady=(10, 2))

        msg_label = ctk.CTkLabel(bubble,
                                 text=text,
                                 font=ctk.CTkFont(family="Segoe UI", size=13),
                                 text_color=self.TEXT_PRIMARY,
                                 justify="left",
                                 wraplength=520)
        msg_label.pack(anchor="w", padx=14, pady=(0, 10))

        self._chat_scroll._parent_canvas.yview_moveto(1.0)
        return msg_label

    def _add_thinking_bubble(self) -> ctk.CTkLabel:
        return self._add_bubble("⏳  Thinking…", is_user=False, animate=False)

    def _show_welcome(self):
        welcome = (
            "👋  Welcome to DocuMind AI!\n\n"
            "Upload a document using the sidebar to get started.\n\n"
            "Once a document is loaded, you can:\n"
            "  •  Ask questions about its content\n"
            "  •  Request a summary or 10 bullet points\n"
            "  •  Extract tables to Excel or a database\n"
            "  •  Extract all figures/images to a folder\n"
            "  •  Run full agentic data ingestion\n\n"
            "All sessions and chat history are saved automatically."
        )
        self._add_bubble(welcome, is_user=False, animate=False)

    # ─────────────────────────────── Send ─────────────────────────────────

    def _send_message(self):
        if self._is_processing:
            return
        query = self._input_box.get().strip()
        if not query:
            return
        if not self._session_id:
            messagebox.showwarning("No Document", "Please upload a document first.")
            return

        # ── Guard: warn user if no API key is set before even trying ─────
        if config.ACTIVE_PROVIDER != "Ollama" and not config.get_active_api_key():
            messagebox.showwarning(
                "API Key Missing",
                f"No {config.ACTIVE_PROVIDER} API key is set.\n\n"
                "Go to ⚙ Settings, paste your API key, and click ⚡ Apply Now.\n"
                "Then try again — no restart needed."
            )
            return

        self._input_box.delete(0, "end")
        self._add_bubble(query, is_user=True)
        self._log_message("user", query)

        thinking = self._add_thinking_bubble()
        self._run_in_thread(self._rag_query, thinking, query)

    def _rag_query(self, query: str) -> str:
        """
        Calls query_document with NO api_key argument.
        rag_engine.py reads the live key from config internally.
        """
        from core.rag_engine import query_document
        return query_document(
            session_id=self._session_id,
            query=query
            # api_key intentionally omitted — rag_engine reads config directly
        )

    # ─────────────────────────── Quick Actions ────────────────────────────

    def _action_summarize(self):
        if not self._guard():
            return
        prompt = (
            "Please provide a concise yet comprehensive summary of this document. "
            "Cover the main topic, key findings or arguments, and any important conclusions."
        )
        self._add_bubble("📝  Summarize this document", is_user=True)
        self._log_message("user", "Summarize this document")
        thinking = self._add_thinking_bubble()
        self._run_in_thread(self._rag_query, thinking, prompt)

    def _action_bullets(self):
        if not self._guard():
            return
        prompt = (
            "Extract exactly 10 key bullet points that capture the most important "
            "information from this document. Format as a numbered list."
        )
        self._add_bubble("🔟  Give me 10 bullet-point summary", is_user=True)
        self._log_message("user", "10 bullet-point summary")
        thinking = self._add_thinking_bubble()
        self._run_in_thread(self._rag_query, thinking, prompt)

    def _action_extract_tables(self):
        if not self._guard():
            return
        if not self._session_file_path:
            messagebox.showwarning("No File Path",
                                   "The original file path is not stored for this session.")
            return

        choice = simpledialog.askstring(
            "Export Format",
            "Where do you want to save the extracted tables?\n\n"
            "Type  excel  for an Excel workbook (.xlsx)\n"
            "Type  sql    to save to the database\n",
            initialvalue="excel"
        )
        if not choice:
            return
        choice = choice.strip().lower()
        if choice not in ("excel", "sql"):
            messagebox.showwarning("Invalid Choice", "Please enter 'excel' or 'sql'.")
            return

        self._add_bubble(f"📊  Extracting all tables → {choice.upper()} format…", is_user=True)
        thinking = self._add_thinking_bubble()
        self._run_in_thread(self._do_extract_tables, thinking, choice)

    def _do_extract_tables(self, export_format: str) -> str:
        from core.parser import extract_pdf_tables, extract_docx_tables
        from storage.exporter import export_tables_to_excel, export_tables_to_sql

        ext = os.path.splitext(self._session_file_path)[1].lower()
        if ext == ".pdf":
            tables = extract_pdf_tables(self._session_file_path)
        elif ext == ".docx":
            tables = extract_docx_tables(self._session_file_path)
        else:
            return "⚠️  Table extraction is supported for PDF and DOCX files only."

        if not tables:
            return "ℹ️  No tables were detected in this document."

        base_name  = os.path.splitext(os.path.basename(self._session_file_path))[0]
        export_dir = str(config.EXPORT_DIR)
        os.makedirs(export_dir, exist_ok=True)

        if export_format == "excel":
            out_path = os.path.join(export_dir, f"{base_name}_tables.xlsx")
            export_tables_to_excel(tables, out_path)
            return (
                f"✅  Extracted {len(tables)} table(s) successfully!\n\n"
                f"📁  Saved to:\n{out_path}\n\n"
                f"Click the folder button below to open the directory."
            )
        else:
            db_url = config.DATABASE_URL
            result = export_tables_to_sql(tables, db_url, base_name)
            if result["status"] == "success":
                s = result["stats"]
                return (
                    f"✅  Exported {s['inserted_tables']} table(s) → "
                    f"{s['rows_inserted']} rows to the database successfully!\n\n"
                    f"Database: {db_url}"
                )
            else:
                return f"❌  SQL export failed: {result.get('message', 'Unknown error')}"

    def _action_extract_figures(self):
        if not self._guard():
            return
        if not self._session_file_path:
            messagebox.showwarning("No File Path",
                                   "The original file path is not stored for this session.")
            return

        self._add_bubble("🖼️  Extracting all figures from the document…", is_user=True)
        thinking = self._add_thinking_bubble()
        self._run_in_thread(self._do_extract_figures, thinking)

    def _do_extract_figures(self) -> str:
        from core.parser import extract_pdf_images, extract_docx_images

        base_name  = os.path.splitext(os.path.basename(self._session_file_path))[0]
        output_dir = os.path.join(str(config.EXPORT_DIR), "figures",
                                  self._session_id[:8])
        os.makedirs(output_dir, exist_ok=True)

        ext = os.path.splitext(self._session_file_path)[1].lower()
        if ext == ".pdf":
            images = extract_pdf_images(self._session_file_path, output_dir)
        elif ext == ".docx":
            images = extract_docx_images(self._session_file_path, output_dir)
        else:
            return "⚠️  Figure extraction is supported for PDF and DOCX files only."

        if not images:
            return "ℹ️  No embedded images/figures were detected in this document."

        return (
            f"✅  Extracted {len(images)} figure(s) successfully!\n\n"
            f"📁  Saved to:\n{output_dir}"
        )

    def _action_agentic_ingest(self):
        if not self._guard():
            return
        if not self._session_file_path:
            messagebox.showwarning("No File Path",
                                   "The original file path is not stored for this session.")
            return

        confirm = messagebox.askyesno(
            "Agentic Ingest",
            "This will run the full LangGraph pipeline:\n\n"
            "  1. Parse and analyze the document structure\n"
            "  2. Discover a database schema via AI\n"
            "  3. Extract all structured records\n"
            "  4. Validate and self-heal data errors\n"
            "  5. Upsert records to your database\n"
            "  6. Export an Excel workbook\n\n"
            "This may take 30–90 seconds. Continue?"
        )
        if not confirm:
            return

        self._add_bubble("🤖  Running Agentic Ingestion Pipeline…", is_user=True)
        thinking = self._add_thinking_bubble()
        self._run_in_thread(self._do_agentic_ingest, thinking)

    def _do_agentic_ingest(self) -> str:
        from core.agent_flow import build_agent_graph

        graph    = build_agent_graph()
        file_ext = os.path.splitext(self._session_file_path)[1].replace(".", "").lower()
        initial_state = {
            "file_path"  : self._session_file_path,
            "file_type"  : file_ext,
            "retry_count": 0
        }

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(graph.ainvoke(initial_state))
            loop.close()
        except Exception as e:
            return f"❌  Agentic pipeline failed:\n{str(e)}"

        status    = result.get("status", "UNKNOWN")
        schema    = result.get("schema_name", "N/A")
        n_records = len(result.get("extracted_data", []))
        db_stats  = result.get("database_upsert_stats", {})
        excel     = result.get("export_path", "N/A")
        errors    = result.get("validation_errors", [])
        retries   = result.get("retry_count", 0)

        lines = [
            f"✅  Agentic Ingestion Complete!\n",
            f"📊  Status:      {status}",
            f"🗄️   Schema:      {schema}",
            f"📋  Records:     {n_records} extracted",
            f"💾  DB Inserted: {db_stats.get('inserted', 0)} / Updated: {db_stats.get('updated', 0)}",
            f"🔁  Self-Heals:  {retries} retries",
            f"📁  Excel:       {excel}",
        ]
        if errors:
            lines.append(f"\n⚠️  Validation issues: {len(errors)}")
            for e in errors[:3]:
                lines.append(f"   • {e}")
            if len(errors) > 3:
                lines.append(f"   … and {len(errors) - 3} more")

        return "\n".join(lines)

    # ────────────────────────────── Threading ─────────────────────────────

    def _run_in_thread(self, task_fn, thinking_label: ctk.CTkLabel, *args):
        self._set_busy(True)

        def worker():
            try:
                result = task_fn(*args)
            except Exception as e:
                import traceback
                traceback.print_exc()
                result = f"❌  An error occurred:\n{str(e)}"
            self.after(0, self._finish_response, thinking_label, result)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_response(self, thinking_label: ctk.CTkLabel, text: str):
        thinking_label.configure(text=text)
        self._log_message("ai", text)
        self._set_busy(False)
        self._chat_scroll._parent_canvas.yview_moveto(1.0)

    def _set_busy(self, busy: bool):
        self._is_processing = busy
        state = "disabled" if busy else "normal"
        self._send_btn.configure(state=state)
        self._input_box.configure(state=state)

    # ────────────────────────────── Helpers ───────────────────────────────

    def _guard(self) -> bool:
        if not self._session_id:
            messagebox.showwarning("No Document", "Please upload a document first.")
            return False
        if self._is_processing:
            messagebox.showinfo("Processing",
                                "Please wait for the current task to complete.")
            return False
        return True

    def _log_message(self, sender: str, message: str):
        if self._session_id:
            from storage.database import log_message
            log_message(self._session_id, sender, message)

    @staticmethod
    def _open_folder(path: str):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

