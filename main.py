# main.py — DocuMind AI Desktop Application Entry Point
import sys
import os

# ── Ensure project root is importable on all platforms ───────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from storage.database import init_db, get_all_sessions
import config


# ─────────────────────────────────────────────────────────────────────────
class DocuMindApp(ctk.CTk):
    """
    Top-level application window.
    Composes the Sidebar and ChatWindow into a two-pane layout and
    orchestrates communication between all UI components.
    """

    # ── Appearance ─────────────────────────────────────────────────────
    BG_COLOR     = "#0f1117"
    CARD_COLOR   = "#1a1d27"
    BORDER_COLOR = "#2a2d3e"
    ACCENT_BLUE  = "#4f8ef7"

    SIDEBAR_WIDTH = 280

    def __init__(self):
        super().__init__()

        # ── App-level appearance ───────────────────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("DocuMind AI  —  Intelligent Document Assistant")
        self.geometry("1280x800")
        self.minsize(960, 620)
        self.configure(fg_color=self.BG_COLOR)
        self._set_window_icon()

        # ── Initialize database ────────────────────────────────────────
        init_db()

        # ── Keep track of the currently loaded file path (for extraction) ─
        self._session_file_map: dict[str, str] = {}   # session_id → file_path

        # ── Build the two-pane layout ──────────────────────────────────
        self._build_layout()

        # ── Keyboard shortcuts ─────────────────────────────────────────
        self.bind("<Control-comma>", lambda e: self._open_settings())

    # ─────────────────────────────── Layout ───────────────────────────────

    def _build_layout(self):
        self.columnconfigure(0, weight=0, minsize=self.SIDEBAR_WIDTH)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Vertical divider between panes ────────────────────────────
        divider = ctk.CTkFrame(self, width=1, fg_color=self.BORDER_COLOR,
                               corner_radius=0)
        divider.grid(row=0, column=0, columnspan=2, sticky="ns",
                     padx=(self.SIDEBAR_WIDTH, 0))

        # ── Sidebar ───────────────────────────────────────────────────
        from ui.sidebar import Sidebar
        self._sidebar = Sidebar(
            self,
            on_session_selected   = self._on_session_selected,
            on_file_indexed       = self._on_file_indexed,
            on_open_settings      = self._open_settings,
            sessions_provider     = get_all_sessions,
            api_key_provider      = lambda: config.GEMINI_API_KEY,
            width=self.SIDEBAR_WIDTH
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        # ── Chat Window ───────────────────────────────────────────────
        from ui.chat_window import ChatWindow
        self._chat = ChatWindow(
            self,
            api_key_provider=lambda: config.GEMINI_API_KEY
        )
        self._chat.grid(row=0, column=1, sticky="nsew")

    # ──────────────────────────── Callbacks ───────────────────────────────

    def _on_session_selected(self, session: dict):
        """Called when the user clicks a session card in the sidebar."""
        sid  = session["session_id"]
        name = session.get("doc_name", "Document")
        path = self._session_file_map.get(sid)
        self._chat.load_session(sid, name, path)

    def _on_file_indexed(self, session_id: str, doc_name: str, file_path: str):
        """Called when background indexing completes successfully."""
        self._session_file_map[session_id] = file_path
        # Auto-switch chat pane to the newly indexed document
        self._chat.load_session(session_id, doc_name, file_path)
        self._sidebar.set_active_session(session_id)

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        SettingsDialog(self)

    # ─────────────────────────────── Misc ─────────────────────────────────

    def _set_window_icon(self):
        """Sets taskbar/title-bar icon if an icon file exists."""
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────
def main():
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = DocuMindApp()
    app.mainloop()


if __name__ == "__main__":
    main()
