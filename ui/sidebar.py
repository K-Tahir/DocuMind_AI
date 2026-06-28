# ui/sidebar.py
import os
import uuid
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

class Sidebar(ctk.CTkFrame):
    """
    Left sidebar component.
    Handles:
      - New / switch chat sessions
      - File upload and background document indexing
      - Settings button
    Communicates with the parent App via callbacks.
    """

    BG_COLOR       = "#0d0f1a"
    CARD_COLOR     = "#1a1d27"
    BORDER_COLOR   = "#2a2d3e"
    ACCENT_BLUE    = "#4f8ef7"
    ACCENT_PURPLE  = "#9d6ff7"
    TEXT_PRIMARY   = "#e8eaf6"
    TEXT_SECONDARY = "#7b7f9e"
    HOVER_COLOR    = "#22253a"
    SUCCESS_COLOR  = "#22c55e"
    WARNING_COLOR  = "#f59e0b"

    SUPPORTED_EXTENSIONS = (
        ("Documents", "*.pdf *.docx *.txt *.csv *.xlsx *.xls"),
        ("PDF Files", "*.pdf"),
        ("Word Documents", "*.docx"),
        ("Text Files", "*.txt"),
        ("Spreadsheets", "*.csv *.xlsx *.xls"),
        ("All Files", "*.*"),
    )

    def __init__(self, parent,
                 on_session_selected,
                 on_file_indexed,
                 on_open_settings,
                 sessions_provider,
                 api_key_provider,
                 **kwargs):
        super().__init__(parent,
                         fg_color=self.BG_COLOR,
                         corner_radius=0,
                         border_width=0,
                         **kwargs)

        self._on_session_selected = on_session_selected
        self._on_file_indexed     = on_file_indexed
        self._on_open_settings    = on_open_settings
        self._sessions_provider   = sessions_provider      # callable → list[dict]
        self._api_key_provider    = api_key_provider       # callable → str
        self._active_session_id   = None

        self._build_ui()
        self.refresh_sessions()

    # ──────────────────────────────── Layout ──────────────────────────────

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # ── App Logo / Brand ──────────────────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
                             corner_radius=0, height=70)
        brand.grid(row=0, column=0, sticky="ew")
        brand.grid_propagate(False)

        logo_label = ctk.CTkLabel(brand,
                                   text="🧠  DocuMind AI",
                                   font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                                   text_color=self.ACCENT_BLUE)
        logo_label.pack(pady=20, padx=16, anchor="w")

        # ── Upload Button ─────────────────────────────────────────────────
        upload_frame = ctk.CTkFrame(self, fg_color="transparent")
        upload_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=12)
        upload_frame.columnconfigure(0, weight=1)

        self._upload_btn = ctk.CTkButton(
            upload_frame,
            text="＋  Upload Document",
            height=44, corner_radius=12,
            fg_color=self.ACCENT_BLUE,
            hover_color=self.ACCENT_PURPLE,
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._upload_file
        )
        self._upload_btn.grid(row=0, column=0, sticky="ew")

        self._upload_status = ctk.CTkLabel(
            upload_frame, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.TEXT_SECONDARY,
            wraplength=200
        )
        self._upload_status.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # ── Progress Bar (hidden by default) ─────────────────────────────
        self._progress = ctk.CTkProgressBar(
            upload_frame, height=4,
            progress_color=self.ACCENT_BLUE,
            fg_color=self.BORDER_COLOR,
            corner_radius=2
        )

        # ── Section Title: Sessions ───────────────────────────────────────
        ctk.CTkLabel(self,
                     text="SESSIONS",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.TEXT_SECONDARY
                     ).grid(row=2, column=0, sticky="w", padx=16, pady=(4, 2))

        # ── Session Scroll Area ───────────────────────────────────────────
        self._session_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=self.BORDER_COLOR,
            scrollbar_button_hover_color=self.ACCENT_BLUE
        )
        self._session_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=0)
        self._session_frame.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # ── Bottom Settings Button ────────────────────────────────────────
        settings_frame = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
                                      corner_radius=0, height=56)
        settings_frame.grid(row=4, column=0, sticky="ew")
        settings_frame.grid_propagate(False)

        ctk.CTkButton(
            settings_frame,
            text="⚙   Settings",
            height=36, corner_radius=10,
            fg_color=self.BORDER_COLOR,
            hover_color="#3a3d4e",
            text_color=self.TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=self._on_open_settings
        ).pack(padx=12, pady=10, fill="x")

    # ────────────────────────────── Session Cards ──────────────────────────

    def refresh_sessions(self):
        """Re-renders the session list from the database."""
        for widget in self._session_frame.winfo_children():
            widget.destroy()

        sessions = self._sessions_provider()
        if not sessions:
            ctk.CTkLabel(self._session_frame,
                         text="No sessions yet.\nUpload a document to begin.",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=self.TEXT_SECONDARY,
                         justify="left"
                         ).grid(row=0, column=0, pady=20, padx=8)
            return

        for i, session in enumerate(sessions):
            self._make_session_card(session, row=i)

    def _make_session_card(self, session: dict, row: int):
        sid   = session["session_id"]
        dname = session.get("doc_name", "Untitled Document")
        ts    = session.get("created_at", "")

        is_active = (sid == self._active_session_id)
        bg = self.HOVER_COLOR if is_active else "transparent"
        border = self.ACCENT_BLUE if is_active else "transparent"

        card = ctk.CTkFrame(self._session_frame, fg_color=bg,
                            corner_radius=10, border_color=self.ACCENT_BLUE if is_active else self.BORDER_COLOR,
                            border_width=1 if is_active else 0)
        card.grid(row=row, column=0, sticky="ew", padx=4, pady=3)
        card.columnconfigure(0, weight=1)

        # Truncate long file names
        display_name = dname if len(dname) <= 28 else dname[:25] + "…"

        ctk.CTkLabel(card,
                     text=f"📄  {display_name}",
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=self.ACCENT_BLUE if is_active else self.TEXT_PRIMARY,
                     anchor="w"
                     ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))

        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                ts_str = dt.strftime("%b %d, %Y  %H:%M")
            except Exception:
                ts_str = ts[:16]
            ctk.CTkLabel(card,
                         text=ts_str,
                         font=ctk.CTkFont(family="Segoe UI", size=10),
                         text_color=self.TEXT_SECONDARY,
                         anchor="w"
                         ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

        # Bind click anywhere on card
        for widget in [card] + card.winfo_children():
            widget.bind("<Button-1>", lambda e, s=session: self._select_session(s))
            widget.bind("<Enter>",    lambda e, f=card: f.configure(fg_color=self.HOVER_COLOR))
            widget.bind("<Leave>",    lambda e, f=card, b=bg: f.configure(fg_color=b))

    # ────────────────────────────── Actions ───────────────────────────────

    def _select_session(self, session: dict):
        self._active_session_id = session["session_id"]
        self.refresh_sessions()
        self._on_session_selected(session)

    def _upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Document to Upload",
            filetypes=self.SUPPORTED_EXTENSIONS
        )
        if not file_path:
            return

        # Create a new session
        session_id = str(uuid.uuid4())
        doc_name   = os.path.basename(file_path)

        # Persist session to DB
        from storage.database import create_session
        create_session(session_id, doc_name)

        # Refresh sidebar immediately
        self._active_session_id = session_id
        self.refresh_sessions()

        # Show progress UI
        self._upload_btn.configure(state="disabled", text="⏳  Indexing…")
        self._upload_status.configure(text=f"Processing: {doc_name}", text_color=self.WARNING_COLOR)
        self._progress.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self._progress.set(0)
        self._progress.start()

        # Background indexing thread
        api_key = self._api_key_provider()
        thread = threading.Thread(
            target=self._index_document,
            args=(file_path, session_id, doc_name, api_key),
            daemon=True
        )
        thread.start()

    def _index_document(self, file_path: str, session_id: str, doc_name: str, api_key: str):
        """Runs in a background thread — parses and indexes the document into ChromaDB."""
        try:
            from core.rag_engine import process_and_index_doc
            process_and_index_doc(file_path, session_id, api_key)

            # Notify on success (must schedule onto main thread)
            self.after(0, self._on_index_success, session_id, doc_name, file_path)
        except Exception as e:
            self.after(0, self._on_index_error, str(e))

    def _on_index_success(self, session_id: str, doc_name: str, file_path: str):
        self._progress.stop()
        self._progress.grid_remove()
        self._upload_btn.configure(state="normal", text="＋  Upload Document")
        self._upload_status.configure(
            text=f"✓  {doc_name} ready!",
            text_color=self.SUCCESS_COLOR
        )
        self.after(3000, lambda: self._upload_status.configure(text=""))
        self._on_file_indexed(session_id, doc_name, file_path)

    def _on_index_error(self, error_msg: str):
        self._progress.stop()
        self._progress.grid_remove()
        self._upload_btn.configure(state="normal", text="＋  Upload Document")
        self._upload_status.configure(text=f"⚠  Error: {error_msg[:60]}", text_color="#ef4444")
        messagebox.showerror("Indexing Failed",
                             f"Failed to process the document.\n\n{error_msg}")

    def set_active_session(self, session_id: str):
        self._active_session_id = session_id
        self.refresh_sessions()
