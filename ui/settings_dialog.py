# # ui/settings_dialog.py
# import customtkinter as ctk
# from tkinter import filedialog
# import config

# class SettingsDialog(ctk.CTkToplevel):
#     """
#     Modal dialog for configuring application settings.
#     Allows the user to update their Gemini API Key, database connection URL,
#     and default export directory. Settings are persisted to settings.json.
#     """

#     # Color Palette (matches main app)
#     BG_COLOR       = "#0f1117"
#     CARD_COLOR     = "#1a1d27"
#     BORDER_COLOR   = "#2a2d3e"
#     ACCENT_BLUE    = "#4f8ef7"
#     ACCENT_PURPLE  = "#9d6ff7"
#     TEXT_PRIMARY   = "#e8eaf6"
#     TEXT_SECONDARY = "#7b7f9e"
#     SUCCESS_COLOR  = "#22c55e"
#     WARNING_COLOR  = "#f59e0b"
#     DANGER_COLOR   = "#ef4444"

#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("DocuMind AI — Settings")
#         self.geometry("640x480")
#         self.resizable(False, False)
#         self.configure(fg_color=self.BG_COLOR)
#         self.grab_set()    # make it modal
#         self.focus_force()

#         # Load current settings
#         self._settings = config.load_settings()
#         self._saved = False

#         self._build_ui()
#         self._center()

#     # ─────────────────────────────── Layout ───────────────────────────────

#     def _build_ui(self):
#         # Header
#         header = ctk.CTkFrame(self, fg_color=self.CARD_COLOR, corner_radius=0,
#                               border_width=0, height=64)
#         header.pack(fill="x", padx=0, pady=0)
#         header.pack_propagate(False)

#         ctk.CTkLabel(header,
#                      text="⚙   Application Settings",
#                      font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
#                      text_color=self.TEXT_PRIMARY).pack(side="left", padx=24, pady=18)

#         # Body
#         body = ctk.CTkScrollableFrame(self, fg_color=self.BG_COLOR,
#                                       scrollbar_button_color=self.BORDER_COLOR)
#         body.pack(fill="both", expand=True, padx=20, pady=(16, 0))

#         # ── Gemini API Key ──────────────────────────────────────────────
#         self._section(body, "🔑  Gemini API Key", row=0)
#         self._api_key_var = ctk.StringVar(value=self._settings.get("gemini_api_key", ""))
#         api_row = ctk.CTkFrame(body, fg_color="transparent")
#         api_row.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 16))
#         api_row.columnconfigure(0, weight=1)

#         self._api_entry = ctk.CTkEntry(api_row,
#                                        textvariable=self._api_key_var,
#                                        show="•",
#                                        placeholder_text="Enter your Gemini API Key...",
#                                        font=ctk.CTkFont(family="Segoe UI", size=13),
#                                        fg_color=self.CARD_COLOR,
#                                        border_color=self.BORDER_COLOR,
#                                        text_color=self.TEXT_PRIMARY,
#                                        height=40, corner_radius=10)
#         self._api_entry.grid(row=0, column=0, sticky="ew")

#         ctk.CTkButton(api_row, text="Show / Hide",
#                       width=100, height=40, corner_radius=10,
#                       fg_color=self.BORDER_COLOR,
#                       hover_color="#3a3d4e",
#                       text_color=self.TEXT_PRIMARY,
#                       font=ctk.CTkFont(family="Segoe UI", size=12),
#                       command=self._toggle_api_key_visibility
#                       ).grid(row=0, column=1, sticky="e", padx=(8, 0))

#         ctk.CTkLabel(body,
#                      text="Used for document Q&A, summarization, and embeddings via Google Gemini.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(0, 20))

#         # ── Database URL ─────────────────────────────────────────────────
#         self._section(body, "🗄️  Database Connection URL", row=3)
#         self._db_url_var = ctk.StringVar(value=self._settings.get("database_url", ""))
#         ctk.CTkEntry(body,
#                      textvariable=self._db_url_var,
#                      placeholder_text="sqlite:///path or postgresql://user:pass@host/db",
#                      font=ctk.CTkFont(family="Segoe UI", size=13),
#                      fg_color=self.CARD_COLOR,
#                      border_color=self.BORDER_COLOR,
#                      text_color=self.TEXT_PRIMARY,
#                      height=40, corner_radius=10
#                      ).grid(row=4, column=0, sticky="ew", pady=(0, 4))

#         ctk.CTkLabel(body,
#                      text="SQLite is used by default. You can point this to PostgreSQL or MySQL.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY).grid(row=5, column=0, sticky="w", pady=(0, 20))

#         # ── Export Directory ──────────────────────────────────────────────
#         self._section(body, "📁  Default Export Directory", row=6)
#         self._export_dir_var = ctk.StringVar(value=self._settings.get("export_dir", ""))

#         dir_row = ctk.CTkFrame(body, fg_color="transparent")
#         dir_row.grid(row=7, column=0, sticky="ew", padx=0, pady=(0, 4))
#         dir_row.columnconfigure(0, weight=1)

#         ctk.CTkEntry(dir_row,
#                      textvariable=self._export_dir_var,
#                      font=ctk.CTkFont(family="Segoe UI", size=13),
#                      fg_color=self.CARD_COLOR,
#                      border_color=self.BORDER_COLOR,
#                      text_color=self.TEXT_PRIMARY,
#                      height=40, corner_radius=10
#                      ).grid(row=0, column=0, sticky="ew")

#         ctk.CTkButton(dir_row, text="Browse…",
#                       width=90, height=40, corner_radius=10,
#                       fg_color=self.BORDER_COLOR,
#                       hover_color="#3a3d4e",
#                       text_color=self.TEXT_PRIMARY,
#                       font=ctk.CTkFont(family="Segoe UI", size=12),
#                       command=self._browse_directory
#                       ).grid(row=0, column=1, padx=(8, 0))

#         ctk.CTkLabel(body,
#                      text="Tables and figures extracted from documents will be saved here.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY).grid(row=8, column=0, sticky="w", pady=(0, 20))

#         # Configure grid column
#         body.columnconfigure(0, weight=1)

#         # ── Footer Buttons ────────────────────────────────────────────────
#         footer = ctk.CTkFrame(self, fg_color=self.CARD_COLOR, corner_radius=0,
#                               border_width=0, height=68)
#         footer.pack(fill="x", side="bottom")
#         footer.pack_propagate(False)

#         self._status_label = ctk.CTkLabel(footer, text="",
#                                           font=ctk.CTkFont(family="Segoe UI", size=12),
#                                           text_color=self.SUCCESS_COLOR)
#         self._status_label.pack(side="left", padx=24)

#         ctk.CTkButton(footer, text="Cancel",
#                       width=100, height=38, corner_radius=10,
#                       fg_color=self.BORDER_COLOR,
#                       hover_color="#3a3d4e",
#                       text_color=self.TEXT_PRIMARY,
#                       font=ctk.CTkFont(family="Segoe UI", size=13),
#                       command=self.destroy
#                       ).pack(side="right", padx=(8, 20), pady=14)

#         ctk.CTkButton(footer, text="Save Settings",
#                       width=130, height=38, corner_radius=10,
#                       fg_color=self.ACCENT_BLUE,
#                       hover_color=self.ACCENT_PURPLE,
#                       text_color="#ffffff",
#                       font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#                       command=self._save
#                       ).pack(side="right", pady=14)

#     # ─────────────────────────────── Helpers ──────────────────────────────

#     def _section(self, parent, text: str, row: int):
#         ctk.CTkLabel(parent, text=text,
#                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#                      text_color=self.TEXT_PRIMARY
#                      ).grid(row=row, column=0, sticky="w", pady=(8, 6))

#     def _toggle_api_key_visibility(self):
#         current = self._api_entry.cget("show")
#         self._api_entry.configure(show="" if current == "•" else "•")

#     def _browse_directory(self):
#         path = filedialog.askdirectory(title="Select Export Directory")
#         if path:
#             self._export_dir_var.set(path)

#     def _save(self):
#         new_settings = {
#             "gemini_api_key": self._api_key_var.get().strip(),
#             "database_url": self._db_url_var.get().strip(),
#             "export_dir": self._export_dir_var.get().strip()
#         }
#         if config.save_settings(new_settings):
#             # Refresh in-memory config values
#             config.GEMINI_API_KEY = new_settings["gemini_api_key"]
#             config.DATABASE_URL = new_settings["database_url"]
#             self._saved = True
#             self._status_label.configure(text="✓  Settings saved successfully!")
#             self.after(1500, self.destroy)
#         else:
#             self._status_label.configure(
#                 text="⚠  Failed to save settings.",
#                 text_color=self.DANGER_COLOR)

#     def _center(self):
#         self.update_idletasks()
#         w, h = 640, 480
#         sw = self.winfo_screenwidth()
#         sh = self.winfo_screenheight()
#         x = (sw - w) // 2
#         y = (sh - h) // 2
#         self.geometry(f"{w}x{h}+{x}+{y}")



# Version: 2
# ui/settings_dialog.py
# import customtkinter as ctk
# from tkinter import filedialog, messagebox
# import config


# class SettingsDialog(ctk.CTkToplevel):
#     """
#     Modal dialog for configuring application settings.
#     API key is always encrypted at rest via Fernet (config.py).
#     Supports paste-and-apply workflow for quick key updates.
#     """

#     # ── Color Palette ──────────────────────────────────────────────────────
#     BG_COLOR       = "#0f1117"
#     CARD_COLOR     = "#1a1d27"
#     BORDER_COLOR   = "#2a2d3e"
#     ACCENT_BLUE    = "#4f8ef7"
#     ACCENT_PURPLE  = "#9d6ff7"
#     TEXT_PRIMARY   = "#e8eaf6"
#     TEXT_SECONDARY = "#7b7f9e"
#     SUCCESS_COLOR  = "#22c55e"
#     WARNING_COLOR  = "#f59e0b"
#     DANGER_COLOR   = "#ef4444"

#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("DocuMind AI — Settings")
#         self.geometry("660x580")
#         self.resizable(False, False)
#         self.configure(fg_color=self.BG_COLOR)
#         self.grab_set()
#         self.focus_force()

#         # Load current settings — gemini_api_key is already decrypted here
#         self._settings = config.load_settings()
#         self._saved    = False

#         self._build_ui()
#         self._center()

#     # ─────────────────────────────── Layout ───────────────────────────────

#     def _build_ui(self):

#         # ── Header ────────────────────────────────────────────────────────
#         header = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=64)
#         header.pack(fill="x")
#         header.pack_propagate(False)

#         ctk.CTkLabel(header,
#                      text="⚙   Application Settings",
#                      font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
#                      text_color=self.TEXT_PRIMARY
#                      ).pack(side="left", padx=24, pady=18)

#         # ── Scrollable Body ───────────────────────────────────────────────
#         body = ctk.CTkScrollableFrame(self, fg_color=self.BG_COLOR,
#                                       scrollbar_button_color=self.BORDER_COLOR)
#         body.pack(fill="both", expand=True, padx=20, pady=(16, 0))
#         body.columnconfigure(0, weight=1)

#         # ── Section 1 : Gemini API Key ────────────────────────────────────
#         self._section(body, "🔑  Gemini API Key", row=0)

#         # Show a masked placeholder if a key is already saved
#         existing_key = self._settings.get("gemini_api_key", "")
#         placeholder  = "●●●●●●●●  (key saved — paste new key to replace)"  \
#                        if existing_key else "Paste your Gemini API Key here…"

#         self._api_key_var = ctk.StringVar()          # intentionally empty on open
#         api_row = ctk.CTkFrame(body, fg_color="transparent")
#         api_row.grid(row=1, column=0, sticky="ew", pady=(0, 4))
#         api_row.columnconfigure(0, weight=1)

#         self._api_entry = ctk.CTkEntry(
#             api_row,
#             textvariable=self._api_key_var,
#             show="•",
#             placeholder_text=placeholder,
#             font=ctk.CTkFont(family="Segoe UI", size=13),
#             fg_color=self.CARD_COLOR,
#             border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=42, corner_radius=10
#         )
#         self._api_entry.grid(row=0, column=0, sticky="ew")

#         # Show / Hide toggle
#         ctk.CTkButton(
#             api_row, text="👁  Show",
#             width=90, height=42, corner_radius=10,
#             fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
#             text_color=self.TEXT_PRIMARY,
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             command=self._toggle_key_visibility
#         ).grid(row=0, column=1, padx=(8, 0))

#         # ── Quick Paste-and-Apply bar ─────────────────────────────────────
#         paste_row = ctk.CTkFrame(body, fg_color=self.CARD_COLOR,
#                                  corner_radius=10, border_width=1,
#                                  border_color=self.BORDER_COLOR)
#         paste_row.grid(row=2, column=0, sticky="ew", pady=(8, 4))
#         paste_row.columnconfigure(0, weight=1)

#         ctk.CTkLabel(paste_row,
#                      text="⚡  Quick Apply  —  paste key above then click Apply Now "
#                           "to encrypt & activate without closing settings.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY,
#                      wraplength=460, justify="left"
#                      ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 6))

#         self._apply_btn = ctk.CTkButton(
#             paste_row,
#             text="⚡  Apply Now",
#             width=120, height=34, corner_radius=8,
#             fg_color=self.ACCENT_BLUE, hover_color=self.ACCENT_PURPLE,
#             text_color="#ffffff",
#             font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
#             command=self._apply_api_key_now
#         )
#         self._apply_btn.grid(row=0, column=1, padx=(8, 12), pady=8)

#         self._apply_status = ctk.CTkLabel(
#             paste_row, text="",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.SUCCESS_COLOR
#         )
#         self._apply_status.grid(row=1, column=0, columnspan=2,
#                                 sticky="w", padx=12, pady=(0, 8))

#         # Hint label
#         ctk.CTkLabel(body,
#                      text="🔒  Your API key is encrypted with AES-128 (Fernet) and "
#                           "never stored in plain text.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY
#                      ).grid(row=3, column=0, sticky="w", pady=(2, 18))

#         # ── Section 2 : Database URL ──────────────────────────────────────
#         self._section(body, "🗄️  Database Connection URL", row=4)
#         self._db_url_var = ctk.StringVar(
#             value=self._settings.get("database_url", ""))
#         ctk.CTkEntry(body,
#                      textvariable=self._db_url_var,
#                      placeholder_text="sqlite:///path  or  postgresql://user:pass@host/db",
#                      font=ctk.CTkFont(family="Segoe UI", size=13),
#                      fg_color=self.CARD_COLOR, border_color=self.BORDER_COLOR,
#                      text_color=self.TEXT_PRIMARY,
#                      height=40, corner_radius=10
#                      ).grid(row=5, column=0, sticky="ew", pady=(0, 4))

#         ctk.CTkLabel(body,
#                      text="SQLite is used by default. You can point this to PostgreSQL or MySQL.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY
#                      ).grid(row=6, column=0, sticky="w", pady=(0, 18))

#         # ── Section 3 : Export Directory ──────────────────────────────────
#         self._section(body, "📁  Default Export Directory", row=7)
#         self._export_dir_var = ctk.StringVar(
#             value=self._settings.get("export_dir", ""))

#         dir_row = ctk.CTkFrame(body, fg_color="transparent")
#         dir_row.grid(row=8, column=0, sticky="ew", pady=(0, 4))
#         dir_row.columnconfigure(0, weight=1)

#         ctk.CTkEntry(dir_row,
#                      textvariable=self._export_dir_var,
#                      font=ctk.CTkFont(family="Segoe UI", size=13),
#                      fg_color=self.CARD_COLOR, border_color=self.BORDER_COLOR,
#                      text_color=self.TEXT_PRIMARY,
#                      height=40, corner_radius=10
#                      ).grid(row=0, column=0, sticky="ew")

#         ctk.CTkButton(dir_row, text="Browse…",
#                       width=90, height=40, corner_radius=10,
#                       fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
#                       text_color=self.TEXT_PRIMARY,
#                       font=ctk.CTkFont(family="Segoe UI", size=12),
#                       command=self._browse_directory
#                       ).grid(row=0, column=1, padx=(8, 0))

#         ctk.CTkLabel(body,
#                      text="Tables and figures extracted from documents will be saved here.",
#                      font=ctk.CTkFont(family="Segoe UI", size=11),
#                      text_color=self.TEXT_SECONDARY
#                      ).grid(row=9, column=0, sticky="w", pady=(0, 20))

#         # ── Footer ────────────────────────────────────────────────────────
#         footer = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=68)
#         footer.pack(fill="x", side="bottom")
#         footer.pack_propagate(False)

#         self._status_label = ctk.CTkLabel(
#             footer, text="",
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             text_color=self.SUCCESS_COLOR)
#         self._status_label.pack(side="left", padx=24)

#         ctk.CTkButton(footer, text="Cancel",
#                       width=100, height=38, corner_radius=10,
#                       fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
#                       text_color=self.TEXT_PRIMARY,
#                       font=ctk.CTkFont(family="Segoe UI", size=13),
#                       command=self.destroy
#                       ).pack(side="right", padx=(8, 20), pady=14)

#         ctk.CTkButton(footer, text="Save Settings",
#                       width=130, height=38, corner_radius=10,
#                       fg_color=self.ACCENT_BLUE, hover_color=self.ACCENT_PURPLE,
#                       text_color="#ffffff",
#                       font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#                       command=self._save
#                       ).pack(side="right", pady=14)

#     # ─────────────────────────────── Helpers ──────────────────────────────

#     def _section(self, parent, text: str, row: int):
#         ctk.CTkLabel(parent, text=text,
#                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#                      text_color=self.TEXT_PRIMARY
#                      ).grid(row=row, column=0, sticky="w", pady=(8, 6))

#     def _toggle_key_visibility(self):
#         self._api_entry.configure(
#             show="" if self._api_entry.cget("show") == "•" else "•"
#         )

#     def _browse_directory(self):
#         path = filedialog.askdirectory(title="Select Export Directory")
#         if path:
#             self._export_dir_var.set(path)

#     def _apply_api_key_now(self):
#         """
#         Encrypts and saves ONLY the API key immediately without closing the dialog.
#         Useful for quick paste-and-activate workflow.
#         """
#         new_key = self._api_key_var.get().strip()

#         if not new_key:
#             self._apply_status.configure(
#                 text="⚠  Please paste a key first.",
#                 text_color=self.WARNING_COLOR)
#             return

#         # Build updated settings preserving existing DB URL & export dir
#         updated = {
#             "gemini_api_key": new_key,
#             "database_url"  : self._db_url_var.get().strip()
#                               or self._settings.get("database_url", ""),
#             "export_dir"    : self._export_dir_var.get().strip()
#                               or self._settings.get("export_dir", "")
#         }

#         if config.save_settings(updated):
#             # Refresh in-memory global immediately
#             config.GEMINI_API_KEY = new_key

#             # Clear entry field for security — key is now saved
#             self._api_key_var.set("")
#             self._api_entry.configure(
#                 placeholder_text="●●●●●●●●  (key saved — paste new key to replace)"
#             )
#             self._apply_status.configure(
#                 text="✓  API key encrypted & applied successfully!",
#                 text_color=self.SUCCESS_COLOR)
#             # Auto-clear the status after 4 seconds
#             self.after(4000, lambda: self._apply_status.configure(text=""))
#         else:
#             self._apply_status.configure(
#                 text="⚠  Failed to apply key.",
#                 text_color=self.DANGER_COLOR)

#     def _save(self):
#         """Saves all settings fields. Uses existing saved key if entry is blank."""
#         typed_key = self._api_key_var.get().strip()

#         # If user didn't type a new key, keep the one already encrypted on disk
#         final_key = typed_key if typed_key else self._settings.get("gemini_api_key", "")

#         new_settings = {
#             "gemini_api_key": final_key,
#             "database_url"  : self._db_url_var.get().strip(),
#             "export_dir"    : self._export_dir_var.get().strip()
#         }

#         if config.save_settings(new_settings):
#             config.GEMINI_API_KEY = final_key
#             config.DATABASE_URL   = new_settings["database_url"]
#             self._saved = True
#             self._status_label.configure(
#                 text="✓  Settings saved & encrypted successfully!")
#             self.after(1500, self.destroy)
#         else:
#             self._status_label.configure(
#                 text="⚠  Failed to save settings.",
#                 text_color=self.DANGER_COLOR)

#     def _center(self):
#         self.update_idletasks()
#         w, h = 660, 580
#         sw = self.winfo_screenwidth()
#         sh = self.winfo_screenheight()
#         self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


# Version 3
# ui/settings_dialog.py
# import customtkinter as ctk
# from tkinter import filedialog
# import config


# class SettingsDialog(ctk.CTkToplevel):
#     """
#     Modal settings dialog.
#     Supports per-provider API key entry (Gemini, OpenAI, Claude, Ollama),
#     model selection, and paste-and-apply quick workflow.
#     All keys encrypted at rest via Fernet (config.py).
#     """

#     # ── Color Palette ──────────────────────────────────────────────────────
#     BG_COLOR       = "#0f1117"
#     CARD_COLOR     = "#1a1d27"
#     BORDER_COLOR   = "#2a2d3e"
#     ACCENT_BLUE    = "#4f8ef7"
#     ACCENT_PURPLE  = "#9d6ff7"
#     TEXT_PRIMARY   = "#e8eaf6"
#     TEXT_SECONDARY = "#7b7f9e"
#     SUCCESS_COLOR  = "#22c55e"
#     WARNING_COLOR  = "#f59e0b"
#     DANGER_COLOR   = "#ef4444"

#     # Provider accent colors
#     PROVIDER_COLORS = {
#         "Gemini": "#4285F4",
#         "OpenAI": "#10a37f",
#         "Claude": "#d97706",
#         "Ollama": "#8b5cf6",
#     }

#     # Provider icons
#     PROVIDER_ICONS = {
#         "Gemini": "✦",
#         "OpenAI": "⬡",
#         "Claude": "◈",
#         "Ollama": "⬡",
#     }

#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("DocuMind AI — Settings")
#         self.geometry("700x680")
#         self.resizable(False, False)
#         self.configure(fg_color=self.BG_COLOR)
#         self.grab_set()
#         self.focus_force()

#         self._settings = config.load_settings()
#         self._saved    = False

#         # StringVars for each provider key entry
#         self._key_vars = {
#             "Gemini": ctk.StringVar(),
#             "OpenAI": ctk.StringVar(),
#             "Claude": ctk.StringVar(),
#         }
#         self._key_entries   = {}
#         self._apply_labels  = {}

#         # Active provider selector
#         self._active_provider_var = ctk.StringVar(
#             value=self._settings.get("active_provider", "Gemini")
#         )

#         # Model selectors
#         self._model_vars = {
#             "Gemini": ctk.StringVar(value=self._settings.get("gemini_model", config.PROVIDER_CHAT_MODELS["Gemini"])),
#             "OpenAI": ctk.StringVar(value=self._settings.get("openai_model", config.PROVIDER_CHAT_MODELS["OpenAI"])),
#             "Claude": ctk.StringVar(value=self._settings.get("claude_model", config.PROVIDER_CHAT_MODELS["Claude"])),
#             "Ollama": ctk.StringVar(value=self._settings.get("ollama_model", config.PROVIDER_CHAT_MODELS["Ollama"])),
#         }

#         self._ollama_url_var = ctk.StringVar(
#             value=self._settings.get("ollama_base_url", "http://localhost:11434")
#         )

#         self._build_ui()
#         self._center()

#     # ─────────────────────────────── Layout ───────────────────────────────

#     def _build_ui(self):

#         # ── Header ────────────────────────────────────────────────────────
#         header = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=64)
#         header.pack(fill="x")
#         header.pack_propagate(False)

#         ctk.CTkLabel(
#             header,
#             text="⚙   Application Settings",
#             font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
#             text_color=self.TEXT_PRIMARY
#         ).pack(side="left", padx=24, pady=18)

#         # ── Scrollable Body ───────────────────────────────────────────────
#         body = ctk.CTkScrollableFrame(self, fg_color=self.BG_COLOR,
#                                       scrollbar_button_color=self.BORDER_COLOR)
#         body.pack(fill="both", expand=True, padx=20, pady=(14, 0))
#         body.columnconfigure(0, weight=1)

#         row = 0

#         # ── Section: Active Provider Selector ─────────────────────────────
#         self._section(body, "🤖  Active AI Provider", row=row)
#         row += 1

#         provider_row = ctk.CTkFrame(body, fg_color="transparent")
#         provider_row.grid(row=row, column=0, sticky="ew", pady=(0, 6))
#         row += 1

#         for p in config.SUPPORTED_PROVIDERS:
#             color = self.PROVIDER_COLORS.get(p, self.ACCENT_BLUE)
#             ctk.CTkRadioButton(
#                 provider_row,
#                 text=f"{self.PROVIDER_ICONS.get(p, '●')}  {p}",
#                 variable=self._active_provider_var,
#                 value=p,
#                 font=ctk.CTkFont(family="Segoe UI", size=13),
#                 text_color=self.TEXT_PRIMARY,
#                 fg_color=color,
#                 border_color=color,
#                 hover_color=color
#             ).pack(side="left", padx=(0, 20))

#         ctk.CTkLabel(
#             body,
#             text="The selected provider will be used for both Q&A and document indexing.",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.TEXT_SECONDARY
#         ).grid(row=row, column=0, sticky="w", pady=(0, 16))
#         row += 1

#         # ── Section: API Keys per Provider ────────────────────────────────
#         self._section(body, "🔑  API Keys", row=row)
#         row += 1

#         # Gemini, OpenAI, Claude each get their own entry + apply button
#         for provider in ["Gemini", "OpenAI", "Claude"]:
#             row = self._build_key_row(body, provider, row)

#         # ── Ollama (no key — just URL + model) ────────────────────────────
#         ollama_frame = ctk.CTkFrame(body, fg_color=self.CARD_COLOR,
#                                     corner_radius=10, border_width=1,
#                                     border_color=self.BORDER_COLOR)
#         ollama_frame.grid(row=row, column=0, sticky="ew", pady=(4, 12))
#         ollama_frame.columnconfigure(1, weight=1)
#         row += 1

#         ctk.CTkLabel(
#             ollama_frame,
#             text=f"{self.PROVIDER_ICONS['Ollama']}  Ollama",
#             font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
#             text_color=self.PROVIDER_COLORS["Ollama"]
#         ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

#         ctk.CTkLabel(
#             ollama_frame,
#             text="Runs locally — no API key needed. Set model and base URL below.",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.TEXT_SECONDARY
#         ).grid(row=0, column=1, columnspan=2, padx=8, pady=(10, 4), sticky="w")

#         ctk.CTkLabel(
#             ollama_frame, text="Base URL:",
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             text_color=self.TEXT_PRIMARY
#         ).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

#         ctk.CTkEntry(
#             ollama_frame,
#             textvariable=self._ollama_url_var,
#             placeholder_text="http://localhost:11434",
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             fg_color=self.BG_COLOR, border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=36, corner_radius=8
#         ).grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(0, 10))

#         ctk.CTkLabel(
#             ollama_frame, text="Model:",
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             text_color=self.TEXT_PRIMARY
#         ).grid(row=2, column=0, padx=12, pady=(0, 10), sticky="w")

#         ctk.CTkEntry(
#             ollama_frame,
#             textvariable=self._model_vars["Ollama"],
#             placeholder_text="llama3",
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             fg_color=self.BG_COLOR, border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=36, corner_radius=8
#         ).grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=(0, 10))

#         # Encryption notice
#         ctk.CTkLabel(
#             body,
#             text="🔒  All API keys are encrypted with AES-128 (Fernet) — never stored in plain text.",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.TEXT_SECONDARY
#         ).grid(row=row, column=0, sticky="w", pady=(0, 18))
#         row += 1

#         # ── Section: Database URL ──────────────────────────────────────────
#         self._section(body, "🗄️  Database Connection URL", row=row)
#         row += 1

#         self._db_url_var = ctk.StringVar(
#             value=self._settings.get("database_url", ""))
#         ctk.CTkEntry(
#             body,
#             textvariable=self._db_url_var,
#             placeholder_text="sqlite:///path  or  postgresql://user:pass@host/db",
#             font=ctk.CTkFont(family="Segoe UI", size=13),
#             fg_color=self.CARD_COLOR, border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=40, corner_radius=10
#         ).grid(row=row, column=0, sticky="ew", pady=(0, 4))
#         row += 1

#         ctk.CTkLabel(
#             body,
#             text="SQLite is used by default. You can switch to PostgreSQL or MySQL.",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.TEXT_SECONDARY
#         ).grid(row=row, column=0, sticky="w", pady=(0, 18))
#         row += 1

#         # ── Section: Export Directory ──────────────────────────────────────
#         self._section(body, "📁  Default Export Directory", row=row)
#         row += 1

#         self._export_dir_var = ctk.StringVar(
#             value=self._settings.get("export_dir", ""))

#         dir_row = ctk.CTkFrame(body, fg_color="transparent")
#         dir_row.grid(row=row, column=0, sticky="ew", pady=(0, 4))
#         dir_row.columnconfigure(0, weight=1)
#         row += 1

#         ctk.CTkEntry(
#             dir_row,
#             textvariable=self._export_dir_var,
#             font=ctk.CTkFont(family="Segoe UI", size=13),
#             fg_color=self.CARD_COLOR, border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=40, corner_radius=10
#         ).grid(row=0, column=0, sticky="ew")

#         ctk.CTkButton(
#             dir_row, text="Browse…",
#             width=90, height=40, corner_radius=10,
#             fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
#             text_color=self.TEXT_PRIMARY,
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             command=self._browse_directory
#         ).grid(row=0, column=1, padx=(8, 0))

#         ctk.CTkLabel(
#             body,
#             text="Extracted tables and figures will be saved here.",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.TEXT_SECONDARY
#         ).grid(row=row, column=0, sticky="w", pady=(0, 20))

#         # ── Footer ────────────────────────────────────────────────────────
#         footer = ctk.CTkFrame(self, fg_color=self.CARD_COLOR,
#                               corner_radius=0, height=68)
#         footer.pack(fill="x", side="bottom")
#         footer.pack_propagate(False)

#         self._status_label = ctk.CTkLabel(
#             footer, text="",
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             text_color=self.SUCCESS_COLOR)
#         self._status_label.pack(side="left", padx=24)

#         ctk.CTkButton(
#             footer, text="Cancel",
#             width=100, height=38, corner_radius=10,
#             fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
#             text_color=self.TEXT_PRIMARY,
#             font=ctk.CTkFont(family="Segoe UI", size=13),
#             command=self.destroy
#         ).pack(side="right", padx=(8, 20), pady=14)

#         ctk.CTkButton(
#             footer, text="Save All Settings",
#             width=150, height=38, corner_radius=10,
#             fg_color=self.ACCENT_BLUE, hover_color=self.ACCENT_PURPLE,
#             text_color="#ffffff",
#             font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#             command=self._save_all
#         ).pack(side="right", pady=14)

#     # ─────────────────────────── Per-Provider Key Row ─────────────────────

#     def _build_key_row(self, parent, provider: str, row: int) -> int:
#         """Builds a collapsible card for one provider's API key + model entry."""
#         color       = self.PROVIDER_COLORS.get(provider, self.ACCENT_BLUE)
#         icon        = self.PROVIDER_ICONS.get(provider, "●")
#         key_field   = f"{provider.lower()}_api_key"
#         has_key     = bool(self._settings.get(key_field, ""))
#         placeholder = "●●●●  key saved — paste to replace" if has_key \
#                       else f"Paste your {provider} API key…"

#         card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR,
#                             corner_radius=10, border_width=1,
#                             border_color=self.BORDER_COLOR)
#         card.grid(row=row, column=0, sticky="ew", pady=(0, 8))
#         card.columnconfigure(1, weight=1)
#         row += 1

#         # Provider label
#         ctk.CTkLabel(
#             card,
#             text=f"{icon}  {provider}",
#             font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
#             text_color=color
#         ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

#         # Key entry
#         entry = ctk.CTkEntry(
#             card,
#             textvariable=self._key_vars[provider],
#             show="•",
#             placeholder_text=placeholder,
#             font=ctk.CTkFont(family="Segoe UI", size=12),
#             fg_color=self.BG_COLOR,
#             border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=36, corner_radius=8
#         )
#         entry.grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=(10, 4))
#         self._key_entries[provider] = entry

#         # Show / Hide
#         ctk.CTkButton(
#             card, text="👁",
#             width=36, height=36, corner_radius=8,
#             fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
#             text_color=self.TEXT_PRIMARY,
#             font=ctk.CTkFont(size=14),
#             command=lambda e=entry: self._toggle_visibility(e)
#         ).grid(row=0, column=2, padx=(0, 6), pady=(10, 4))

#         # Apply Now
#         ctk.CTkButton(
#             card, text="⚡ Apply",
#             width=80, height=36, corner_radius=8,
#             fg_color=color, hover_color=self.ACCENT_PURPLE,
#             text_color="#ffffff",
#             font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
#             command=lambda p=provider: self._apply_key_now(p)
#         ).grid(row=0, column=3, padx=(0, 12), pady=(10, 4))

#         # Model selector label + entry
#         ctk.CTkLabel(
#             card, text="Model:",
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             text_color=self.TEXT_SECONDARY
#         ).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

#         ctk.CTkEntry(
#             card,
#             textvariable=self._model_vars[provider],
#             font=ctk.CTkFont(family="Segoe UI", size=11),
#             fg_color=self.BG_COLOR, border_color=self.BORDER_COLOR,
#             text_color=self.TEXT_PRIMARY,
#             height=30, corner_radius=8
#         ).grid(row=1, column=1, sticky="ew", padx=(0, 6), pady=(0, 10))

#         # Apply status label
#         status_lbl = ctk.CTkLabel(
#             card, text="",
#             font=ctk.CTkFont(family="Segoe UI", size=10),
#             text_color=self.SUCCESS_COLOR
#         )
#         status_lbl.grid(row=1, column=2, columnspan=2,
#                         padx=(0, 12), pady=(0, 10), sticky="e")
#         self._apply_labels[provider] = status_lbl

#         return row

#     # ─────────────────────────────── Helpers ──────────────────────────────

#     def _section(self, parent, text: str, row: int):
#         ctk.CTkLabel(
#             parent, text=text,
#             font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
#             text_color=self.TEXT_PRIMARY
#         ).grid(row=row, column=0, sticky="w", pady=(10, 6))

#     def _toggle_visibility(self, entry: ctk.CTkEntry):
#         entry.configure(show="" if entry.cget("show") == "•" else "•")

#     def _browse_directory(self):
#         path = filedialog.askdirectory(title="Select Export Directory")
#         if path:
#             self._export_dir_var.set(path)

#     def _apply_key_now(self, provider: str):
#         """Encrypts and saves ONLY the key for this provider immediately."""
#         new_key = self._key_vars[provider].get().strip()
#         lbl     = self._apply_labels[provider]

#         if not new_key:
#             lbl.configure(text="⚠  Paste a key first.", text_color=self.WARNING_COLOR)
#             self.after(3000, lambda: lbl.configure(text=""))
#             return

#         # Build a settings dict preserving everything else
#         current = config.load_settings()
#         current[f"{provider.lower()}_api_key"] = new_key
#         current["active_provider"] = self._active_provider_var.get()
#         current["gemini_model"]    = self._model_vars["Gemini"].get()
#         current["openai_model"]    = self._model_vars["OpenAI"].get()
#         current["claude_model"]    = self._model_vars["Claude"].get()
#         current["ollama_model"]    = self._model_vars["Ollama"].get()
#         current["ollama_base_url"] = self._ollama_url_var.get()

#         if config.save_settings(current):
#             # Refresh global in-memory config
#             setattr(config, f"{provider.upper()}_API_KEY", new_key)
#             config.ACTIVE_PROVIDER = self._active_provider_var.get()

#             # Clear entry field — key is now encrypted on disk
#             self._key_vars[provider].set("")
#             entry = self._key_entries.get(provider)
#             if entry:
#                 entry.configure(
#                     placeholder_text="●●●●  key saved — paste to replace")

#             lbl.configure(text="✓  Encrypted & applied!",
#                           text_color=self.SUCCESS_COLOR)
#             self.after(4000, lambda: lbl.configure(text=""))
#         else:
#             lbl.configure(text="✗  Save failed.", text_color=self.DANGER_COLOR)

#     def _save_all(self):
#         """Collects all fields and saves everything at once."""
#         current = config.load_settings()   # base — preserves existing encrypted keys

#         # Only overwrite a key if the user actually typed something new
#         for provider in ["Gemini", "OpenAI", "Claude"]:
#             typed = self._key_vars[provider].get().strip()
#             if typed:
#                 current[f"{provider.lower()}_api_key"] = typed

#         current["active_provider"] = self._active_provider_var.get()
#         current["gemini_model"]    = self._model_vars["Gemini"].get()
#         current["openai_model"]    = self._model_vars["OpenAI"].get()
#         current["claude_model"]    = self._model_vars["Claude"].get()
#         current["ollama_model"]    = self._model_vars["Ollama"].get()
#         current["ollama_base_url"] = self._ollama_url_var.get().strip()
#         current["database_url"]    = self._db_url_var.get().strip()
#         current["export_dir"]      = self._export_dir_var.get().strip()

#         if config.save_settings(current):
#             # Refresh all in-memory globals
#             config.ACTIVE_PROVIDER = current["active_provider"]
#             config.GEMINI_API_KEY  = config.decrypt_value(
#                 config.load_settings().get("gemini_api_key_enc", ""))
#             config.OPENAI_API_KEY  = config.decrypt_value(
#                 config.load_settings().get("openai_api_key_enc", ""))
#             config.CLAUDE_API_KEY  = config.decrypt_value(
#                 config.load_settings().get("claude_api_key_enc", ""))
#             config.OLLAMA_BASE_URL = current["ollama_base_url"]
#             config.DATABASE_URL    = current["database_url"]

#             self._saved = True
#             self._status_label.configure(
#                 text="✓  All settings saved & encrypted!")
#             self.after(1500, self.destroy)
#         else:
#             self._status_label.configure(
#                 text="⚠  Failed to save settings.",
#                 text_color=self.DANGER_COLOR)

#     def _center(self):
#         self.update_idletasks()
#         w, h = 700, 680
#         sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
#         self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


# Version 4

# ui/settings_dialog.py
import customtkinter as ctk
from tkinter import filedialog
import config


class SettingsDialog(ctk.CTkToplevel):
    """
    Modal settings dialog.
    - Per-provider API key entry: Gemini, OpenAI, Claude, Ollama
    - ⚡ Apply Now per provider — encrypts key, saves to disk, injects
      into os.environ immediately. User never touches system env vars.
    - Save All Settings saves everything at once.
    """

    BG_COLOR       = "#0f1117"
    CARD_COLOR     = "#1a1d27"
    BORDER_COLOR   = "#2a2d3e"
    ACCENT_BLUE    = "#4f8ef7"
    ACCENT_PURPLE  = "#9d6ff7"
    TEXT_PRIMARY   = "#e8eaf6"
    TEXT_SECONDARY = "#7b7f9e"
    SUCCESS_COLOR  = "#22c55e"
    WARNING_COLOR  = "#f59e0b"
    DANGER_COLOR   = "#ef4444"

    PROVIDER_COLORS = {
        "Gemini": "#4285F4",
        "OpenAI": "#10a37f",
        "Claude": "#d97706",
        "Ollama": "#8b5cf6",
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.title("DocuMind AI — Settings")
        self.geometry("700x700")
        self.resizable(False, False)
        self.configure(fg_color=self.BG_COLOR)
        self.grab_set()
        self.focus_force()

        # Always load the freshest settings from disk
        self._settings = config.load_settings()

        self._key_vars    = {p: ctk.StringVar() for p in ["Gemini", "OpenAI", "Claude"]}
        self._key_entries = {}
        self._apply_lbls  = {}

        self._active_var = ctk.StringVar(
            value=self._settings.get("active_provider", "Gemini"))

        self._model_vars = {
            p: ctk.StringVar(value=self._settings.get(
                f"{p.lower()}_model", config.PROVIDER_CHAT_MODELS[p]))
            for p in config.SUPPORTED_PROVIDERS
        }
        self._ollama_url_var = ctk.StringVar(
            value=self._settings.get("ollama_base_url", "http://localhost:11434"))

        self._build_ui()
        self._center()

    # ─────────────────────────────── Layout ───────────────────────────────

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=self.CARD_COLOR, corner_radius=0, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⚙   Application Settings",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                     text_color=self.TEXT_PRIMARY
                     ).pack(side="left", padx=24, pady=18)

        # Scrollable body
        body = ctk.CTkScrollableFrame(self, fg_color=self.BG_COLOR,
                                      scrollbar_button_color=self.BORDER_COLOR)
        body.pack(fill="both", expand=True, padx=20, pady=(14, 0))
        body.columnconfigure(0, weight=1)

        row = 0

        # ── Active provider selector ───────────────────────────────────────
        self._section(body, "🤖  Active AI Provider", row); row += 1

        prow = ctk.CTkFrame(body, fg_color="transparent")
        prow.grid(row=row, column=0, sticky="ew", pady=(0, 4)); row += 1

        for p in config.SUPPORTED_PROVIDERS:
            c = self.PROVIDER_COLORS.get(p, self.ACCENT_BLUE)
            ctk.CTkRadioButton(prow, text=p, variable=self._active_var, value=p,
                               font=ctk.CTkFont(family="Segoe UI", size=13),
                               text_color=self.TEXT_PRIMARY,
                               fg_color=c, border_color=c, hover_color=c
                               ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(body,
                     text="Selected provider is used for Q&A, embeddings, and agentic pipeline.",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.TEXT_SECONDARY
                     ).grid(row=row, column=0, sticky="w", pady=(0, 16)); row += 1

        # ── API keys ───────────────────────────────────────────────────────
        self._section(body, "🔑  API Keys", row); row += 1

        for provider in ["Gemini", "OpenAI", "Claude"]:
            row = self._provider_card(body, provider, row)

        # Ollama card
        row = self._ollama_card(body, row)

        ctk.CTkLabel(body,
                     text="🔒  Keys are encrypted with AES-128 Fernet — never stored in plain text.",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.TEXT_SECONDARY
                     ).grid(row=row, column=0, sticky="w", pady=(4, 18)); row += 1

        # ── Database URL ───────────────────────────────────────────────────
        self._section(body, "🗄️  Database Connection URL", row); row += 1
        self._db_url_var = ctk.StringVar(value=self._settings.get("database_url", ""))
        ctk.CTkEntry(body, textvariable=self._db_url_var,
                     placeholder_text="sqlite:///path  or  postgresql://user:pass@host/db",
                     font=ctk.CTkFont(family="Segoe UI", size=13),
                     fg_color=self.CARD_COLOR, border_color=self.BORDER_COLOR,
                     text_color=self.TEXT_PRIMARY, height=40, corner_radius=10
                     ).grid(row=row, column=0, sticky="ew", pady=(0, 4)); row += 1
        ctk.CTkLabel(body, text="SQLite is used by default. Switch to PostgreSQL or MySQL if needed.",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.TEXT_SECONDARY
                     ).grid(row=row, column=0, sticky="w", pady=(0, 18)); row += 1

        # ── Export directory ───────────────────────────────────────────────
        self._section(body, "📁  Default Export Directory", row); row += 1
        self._export_dir_var = ctk.StringVar(value=self._settings.get("export_dir", ""))
        dr = ctk.CTkFrame(body, fg_color="transparent")
        dr.grid(row=row, column=0, sticky="ew", pady=(0, 4)); row += 1
        dr.columnconfigure(0, weight=1)
        ctk.CTkEntry(dr, textvariable=self._export_dir_var,
                     font=ctk.CTkFont(family="Segoe UI", size=13),
                     fg_color=self.CARD_COLOR, border_color=self.BORDER_COLOR,
                     text_color=self.TEXT_PRIMARY, height=40, corner_radius=10
                     ).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(dr, text="Browse…", width=90, height=40, corner_radius=10,
                      fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
                      text_color=self.TEXT_PRIMARY,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      command=self._browse_dir
                      ).grid(row=0, column=1, padx=(8, 0))

        # Footer
        ftr = ctk.CTkFrame(self, fg_color=self.CARD_COLOR, corner_radius=0, height=68)
        ftr.pack(fill="x", side="bottom")
        ftr.pack_propagate(False)

        self._status_lbl = ctk.CTkLabel(ftr, text="",
                                        font=ctk.CTkFont(family="Segoe UI", size=12),
                                        text_color=self.SUCCESS_COLOR)
        self._status_lbl.pack(side="left", padx=24)

        ctk.CTkButton(ftr, text="Cancel", width=100, height=38, corner_radius=10,
                      fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
                      text_color=self.TEXT_PRIMARY,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.destroy
                      ).pack(side="right", padx=(8, 20), pady=14)

        ctk.CTkButton(ftr, text="Save All Settings", width=150, height=38,
                      corner_radius=10, fg_color=self.ACCENT_BLUE,
                      hover_color=self.ACCENT_PURPLE, text_color="#ffffff",
                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                      command=self._save_all
                      ).pack(side="right", pady=14)

    # ─────────────────────── Provider Card Builder ─────────────────────────

    def _provider_card(self, parent, provider: str, row: int) -> int:
        color       = self.PROVIDER_COLORS.get(provider, self.ACCENT_BLUE)
        has_key     = bool(self._settings.get(f"{provider.lower()}_api_key", ""))
        placeholder = "●●●●  key saved — paste new key to replace" \
                      if has_key else f"Paste your {provider} API key…"

        card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=10,
                            border_width=1, border_color=self.BORDER_COLOR)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        card.columnconfigure(1, weight=1)
        row += 1

        # Provider label
        ctk.CTkLabel(card, text=provider,
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=color
                     ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        # Key entry
        entry = ctk.CTkEntry(card, textvariable=self._key_vars[provider],
                             show="•", placeholder_text=placeholder,
                             font=ctk.CTkFont(family="Segoe UI", size=12),
                             fg_color=self.BG_COLOR, border_color=self.BORDER_COLOR,
                             text_color=self.TEXT_PRIMARY, height=36, corner_radius=8)
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=(10, 4))
        self._key_entries[provider] = entry

        # Show/hide
        ctk.CTkButton(card, text="👁", width=36, height=36, corner_radius=8,
                      fg_color=self.BORDER_COLOR, hover_color="#3a3d4e",
                      text_color=self.TEXT_PRIMARY,
                      command=lambda e=entry: e.configure(
                          show="" if e.cget("show") == "•" else "•")
                      ).grid(row=0, column=2, padx=(0, 6), pady=(10, 4))

        # Apply Now
        ctk.CTkButton(card, text="⚡ Apply Now", width=110, height=36,
                      corner_radius=8, fg_color=color, hover_color=self.ACCENT_PURPLE,
                      text_color="#ffffff",
                      font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                      command=lambda p=provider: self._apply_now(p)
                      ).grid(row=0, column=3, padx=(0, 12), pady=(10, 4))

        # Model entry
        ctk.CTkLabel(card, text="Model:",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.TEXT_SECONDARY
                     ).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
        ctk.CTkEntry(card, textvariable=self._model_vars[provider],
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     fg_color=self.BG_COLOR, border_color=self.BORDER_COLOR,
                     text_color=self.TEXT_PRIMARY, height=30, corner_radius=8
                     ).grid(row=1, column=1, sticky="ew", padx=(0, 6), pady=(0, 10))

        # Status label
        lbl = ctk.CTkLabel(card, text="",
                           font=ctk.CTkFont(family="Segoe UI", size=10),
                           text_color=self.SUCCESS_COLOR)
        lbl.grid(row=1, column=2, columnspan=2, padx=(0, 12), pady=(0, 10), sticky="e")
        self._apply_lbls[provider] = lbl

        return row

    def _ollama_card(self, parent, row: int) -> int:
        color = self.PROVIDER_COLORS["Ollama"]
        card  = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=10,
                             border_width=1, border_color=self.BORDER_COLOR)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        card.columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(card, text="Ollama  (local — no API key needed)",
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=color
                     ).grid(row=0, column=0, columnspan=2, padx=12,
                            pady=(10, 4), sticky="w")

        for i, (lbl_text, var, ph) in enumerate([
            ("Base URL:", self._ollama_url_var, "http://localhost:11434"),
            ("Model:",    self._model_vars["Ollama"], "llama3"),
        ], start=1):
            ctk.CTkLabel(card, text=lbl_text,
                         font=ctk.CTkFont(family="Segoe UI", size=11),
                         text_color=self.TEXT_SECONDARY
                         ).grid(row=i, column=0, padx=12, pady=(0, 10), sticky="w")
            ctk.CTkEntry(card, textvariable=var, placeholder_text=ph,
                         font=ctk.CTkFont(family="Segoe UI", size=11),
                         fg_color=self.BG_COLOR, border_color=self.BORDER_COLOR,
                         text_color=self.TEXT_PRIMARY, height=32, corner_radius=8
                         ).grid(row=i, column=1, sticky="ew",
                                padx=(0, 12), pady=(0, 10))

        return row

    # ─────────────────────────────── Actions ──────────────────────────────

    def _apply_now(self, provider: str):
        """
        Encrypts and saves the key for this provider immediately.
        config.save_settings() calls _inject_env_vars() internally,
        so LangChain picks up the key the moment Apply Now is clicked.
        No restart. No manual env var setup.
        """
        new_key = self._key_vars[provider].get().strip()
        lbl     = self._apply_lbls[provider]

        if not new_key:
            lbl.configure(text="⚠  Paste a key first.", text_color=self.WARNING_COLOR)
            self.after(3000, lambda: lbl.configure(text=""))
            return

        # Load current settings so we don't wipe other providers' keys
        current = config.load_settings()
        current[f"{provider.lower()}_api_key"] = new_key
        current["active_provider"] = self._active_var.get()
        for p in config.SUPPORTED_PROVIDERS:
            current[f"{p.lower()}_model"] = self._model_vars[p].get()
        current["ollama_base_url"] = self._ollama_url_var.get().strip()

        # This single call: encrypts → saves → injects into os.environ → refreshes globals
        if config.save_settings(current):
            # Clear the entry for security
            self._key_vars[provider].set("")
            self._key_entries[provider].configure(
                placeholder_text="●●●●  key saved — paste new key to replace")

            lbl.configure(
                text="✓  Encrypted, saved & injected into environment!",
                text_color=self.SUCCESS_COLOR)
            self.after(4000, lambda: lbl.configure(text=""))
        else:
            lbl.configure(text="✗  Save failed.", text_color=self.DANGER_COLOR)

    def _save_all(self):
        """Saves all settings. Blank key fields preserve the existing saved key."""
        current = config.load_settings()

        for provider in ["Gemini", "OpenAI", "Claude"]:
            typed = self._key_vars[provider].get().strip()
            if typed:
                current[f"{provider.lower()}_api_key"] = typed

        current["active_provider"] = self._active_var.get()
        for p in config.SUPPORTED_PROVIDERS:
            current[f"{p.lower()}_model"] = self._model_vars[p].get()
        current["ollama_base_url"] = self._ollama_url_var.get().strip()
        current["database_url"]    = self._db_url_var.get().strip()
        current["export_dir"]      = self._export_dir_var.get().strip()

        # Encrypts, saves, injects env vars, refreshes globals — all in one call
        if config.save_settings(current):
            self._status_lbl.configure(
                text="✓  All settings saved, encrypted & environment updated!")
            self.after(1500, self.destroy)
        else:
            self._status_lbl.configure(
                text="⚠  Failed to save settings.", text_color=self.DANGER_COLOR)

    def _browse_dir(self):
        path = filedialog.askdirectory(title="Select Export Directory")
        if path:
            self._export_dir_var.set(path)

    def _section(self, parent, text: str, row: int):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color=self.TEXT_PRIMARY
                     ).grid(row=row, column=0, sticky="w", pady=(10, 6))

    def _center(self):
        self.update_idletasks()
        w, h = 700, 700
        self.geometry(
            f"{w}x{h}+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}")
