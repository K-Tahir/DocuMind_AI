# Version 1
# # config.py
# import os
# import json
# from pathlib import Path

# # Resolve the user's local AppData directory or home directory for data isolation
# APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "DocIntelTool"
# APP_DIR.mkdir(parents=True, exist_ok=True)

# # Define local operational paths
# DB_PATH = APP_DIR / "app_data.db"
# CHROMA_DIR = str(APP_DIR / "vector_store")
# EXPORT_DIR = APP_DIR / "exports"
# SETTINGS_PATH = APP_DIR / "settings.json"

# EXPORT_DIR.mkdir(exist_ok=True)

# # Default Settings
# db_abs_path = os.path.abspath(DB_PATH).replace("\\", "/")
# DEFAULT_SETTINGS = {
#     "gemini_api_key": "AQ.Ab8RN6J_zI5KE4wCC8jEEsAS7Zt4hXy7EwQv31pfoZ5PdD9bIQ",
#     "database_url": f"sqlite:///{db_abs_path}",
#     "export_dir": str(EXPORT_DIR)
# }

# def load_settings():
#     if SETTINGS_PATH.exists():
#         try:
#             with open(SETTINGS_PATH, "r") as f:
#                 user_settings = json.load(f)
#                 return {**DEFAULT_SETTINGS, **user_settings}
#         except Exception:
#             return DEFAULT_SETTINGS
#     return DEFAULT_SETTINGS

# def save_settings(settings):
#     try:
#         with open(SETTINGS_PATH, "w") as f:
#             json.dump(settings, f, indent=4)
#         return True
#     except Exception as e:
#         print(f"[ERROR] Failed to save settings: {e}")
#         return False

# # Initialize settings
# current_settings = load_settings()

# GEMINI_API_KEY = current_settings.get("gemini_api_key")
# DATABASE_URL = current_settings.get("database_url")
# EXPORT_DIR = Path(current_settings.get("export_dir"))

# print(f"[INFO] Initializing workspace storage at: {APP_DIR}")
# print(f"[INFO] Target Storage: {DATABASE_URL}")






# Version 2

# config.py
# import os
# import json
# from pathlib import Path
# from cryptography.fernet import Fernet

# # ── Workspace Paths ────────────────────────────────────────────────────────
# APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "DocIntelTool"
# APP_DIR.mkdir(parents=True, exist_ok=True)

# DB_PATH      = APP_DIR / "app_data.db"
# CHROMA_DIR   = str(APP_DIR / "vector_store")
# EXPORT_DIR   = APP_DIR / "exports"
# SETTINGS_PATH = APP_DIR / "settings.json"
# KEY_PATH     = APP_DIR / ".secret.key"          # Encryption key — never commit this

# EXPORT_DIR.mkdir(exist_ok=True)

# # ── Encryption Helpers ─────────────────────────────────────────────────────

# def _load_or_create_fernet_key() -> Fernet:
#     """
#     Loads the machine-local Fernet symmetric key from disk.
#     If it doesn't exist yet, generates one and saves it.
#     This key lives only on the user's machine — never in source code or git.
#     """
#     if KEY_PATH.exists():
#         key = KEY_PATH.read_bytes()
#     else:
#         key = Fernet.generate_key()
#         KEY_PATH.write_bytes(key)
#         # Restrict file permissions on non-Windows systems
#         try:
#             os.chmod(KEY_PATH, 0o600)
#         except Exception:
#             pass
#         print(f"[INFO] New encryption key generated at: {KEY_PATH}")
#     return Fernet(key)


# _fernet = _load_or_create_fernet_key()


# def encrypt_value(plain_text: str) -> str:
#     """Encrypts a plain string and returns a UTF-8 encoded token string."""
#     if not plain_text:
#         return ""
#     return _fernet.encrypt(plain_text.encode()).decode()


# def decrypt_value(token: str) -> str:
#     """Decrypts a Fernet token string back to plain text. Returns '' on failure."""
#     if not token:
#         return ""
#     try:
#         return _fernet.decrypt(token.encode()).decode()
#     except Exception:
#         # Token is corrupted or was encrypted with a different key
#         print("[WARNING] Failed to decrypt value — it may have been encrypted with a different key.")
#         return ""


# # ── Default Settings (no real API key hardcoded) ───────────────────────────

# db_abs_path = os.path.abspath(DB_PATH).replace("\\", "/")

# DEFAULT_SETTINGS = {
#     "gemini_api_key_enc": "",          # Stored encrypted — empty by default
#     "database_url": f"sqlite:///{db_abs_path}",
#     "export_dir": str(EXPORT_DIR)
# }


# # ── Settings I/O ───────────────────────────────────────────────────────────

# def load_settings() -> dict:
#     """
#     Loads settings from disk and decrypts the API key before returning.
#     Returns a dict with a plain-text 'gemini_api_key' field ready to use.
#     """
#     if SETTINGS_PATH.exists():
#         try:
#             with open(SETTINGS_PATH, "r") as f:
#                 saved = json.load(f)
#             merged = {**DEFAULT_SETTINGS, **saved}
#         except Exception:
#             merged = DEFAULT_SETTINGS.copy()
#     else:
#         merged = DEFAULT_SETTINGS.copy()

#     # Expose decrypted key under the standard name the rest of the app uses
#     merged["gemini_api_key"] = decrypt_value(merged.get("gemini_api_key_enc", ""))
#     return merged


# def save_settings(settings: dict) -> bool:
#     """
#     Accepts a dict that may contain a plain-text 'gemini_api_key'.
#     Encrypts it before writing to disk — the raw key is NEVER persisted.
#     """
#     to_save = {
#         "gemini_api_key_enc": encrypt_value(settings.get("gemini_api_key", "").strip()),
#         "database_url": settings.get("database_url", DEFAULT_SETTINGS["database_url"]).strip(),
#         "export_dir": settings.get("export_dir", str(EXPORT_DIR)).strip()
#     }
#     try:
#         with open(SETTINGS_PATH, "w") as f:
#             json.dump(to_save, f, indent=4)
#         print("[INFO] Settings saved successfully (API key encrypted).")
#         return True
#     except Exception as e:
#         print(f"[ERROR] Failed to save settings: {e}")
#         return False


# # ── Runtime Config (module-level globals used across the app) ──────────────

# current_settings = load_settings()

# GEMINI_API_KEY = current_settings.get("gemini_api_key", "")
# DATABASE_URL   = current_settings.get("database_url")
# EXPORT_DIR     = Path(current_settings.get("export_dir"))

# print(f"[INFO] Initializing workspace storage at: {APP_DIR}")
# print(f"[INFO] Target Storage: {DATABASE_URL}")
# print(f"[INFO] API Key loaded: {'✓  (set)' if GEMINI_API_KEY else '✗  (not set — please add via Settings)'}")

# Version 3

# config.py
# import os
# import json
# from pathlib import Path
# from cryptography.fernet import Fernet

# # ── Workspace Paths ────────────────────────────────────────────────────────
# APP_DIR       = Path(os.getenv("APPDATA", Path.home())) / "DocIntelTool"
# APP_DIR.mkdir(parents=True, exist_ok=True)

# DB_PATH       = APP_DIR / "app_data.db"
# CHROMA_DIR    = str(APP_DIR / "vector_store")
# EXPORT_DIR    = APP_DIR / "exports"
# SETTINGS_PATH = APP_DIR / "settings.json"
# KEY_PATH      = APP_DIR / ".secret.key"   # Machine-local only — never commit

# EXPORT_DIR.mkdir(exist_ok=True)

# # ── Supported AI Providers ─────────────────────────────────────────────────
# SUPPORTED_PROVIDERS = ["Gemini", "OpenAI", "Claude", "Ollama"]

# # Provider → embedding model defaults
# PROVIDER_EMBEDDING_MODELS = {
#     "Gemini": "models/embedding-001",
#     "OpenAI": "text-embedding-3-small",
#     "Claude": "text-embedding-3-small",   # Claude has no embeddings; falls back to OpenAI
#     "Ollama": "nomic-embed-text",
# }

# # Provider → chat model defaults
# PROVIDER_CHAT_MODELS = {
#     "Gemini": "gemini-2.5-flash",
#     "OpenAI": "gpt-4o",
#     "Claude": "claude-sonnet-4-6",
#     "Ollama": "llama3",
# }

# # ── Encryption Helpers ─────────────────────────────────────────────────────

# def _load_or_create_fernet_key() -> Fernet:
#     """
#     Loads machine-local Fernet symmetric key.
#     Generates and saves one on first run.
#     This key lives ONLY on the user's machine — never in source code or git.
#     """
#     if KEY_PATH.exists():
#         key = KEY_PATH.read_bytes()
#     else:
#         key = Fernet.generate_key()
#         KEY_PATH.write_bytes(key)
#         try:
#             os.chmod(KEY_PATH, 0o600)
#         except Exception:
#             pass
#         print(f"[INFO] New encryption key generated at: {KEY_PATH}")
#     return Fernet(key)


# _fernet = _load_or_create_fernet_key()


# def encrypt_value(plain_text: str) -> str:
#     """Encrypts a plain string → returns a UTF-8 Fernet token."""
#     if not plain_text:
#         return ""
#     return _fernet.encrypt(plain_text.encode()).decode()


# def decrypt_value(token: str) -> str:
#     """Decrypts a Fernet token → plain text. Returns '' on any failure."""
#     if not token:
#         return ""
#     try:
#         return _fernet.decrypt(token.encode()).decode()
#     except Exception:
#         print("[WARNING] Decryption failed — key may have changed.")
#         return ""


# # ── Default Settings ───────────────────────────────────────────────────────

# db_abs_path = os.path.abspath(DB_PATH).replace("\\", "/")

# DEFAULT_SETTINGS = {
#     # Active provider
#     "active_provider"     : "Gemini",

#     # Encrypted API keys per provider (empty by default — NO hardcoded keys)
#     "gemini_api_key_enc"  : "",
#     "openai_api_key_enc"  : "",
#     "claude_api_key_enc"  : "",

#     # Ollama runs locally — no key needed, just a base URL
#     "ollama_base_url"     : "http://localhost:11434",

#     # Selected models per provider
#     "gemini_model"        : PROVIDER_CHAT_MODELS["Gemini"],
#     "openai_model"        : PROVIDER_CHAT_MODELS["OpenAI"],
#     "claude_model"        : PROVIDER_CHAT_MODELS["Claude"],
#     "ollama_model"        : PROVIDER_CHAT_MODELS["Ollama"],

#     # App settings
#     "database_url"        : f"sqlite:///{db_abs_path}",
#     "export_dir"          : str(EXPORT_DIR),
# }


# # ── Settings I/O ───────────────────────────────────────────────────────────

# def load_settings() -> dict:
#     """
#     Loads settings.json and decrypts all API keys before returning.
#     Returns a dict with plain-text '*_api_key' fields ready to use.
#     """
#     if SETTINGS_PATH.exists():
#         try:
#             with open(SETTINGS_PATH, "r") as f:
#                 saved = json.load(f)
#             merged = {**DEFAULT_SETTINGS, **saved}
#         except Exception:
#             merged = DEFAULT_SETTINGS.copy()
#     else:
#         merged = DEFAULT_SETTINGS.copy()

#     # Expose decrypted keys under plain names for use across the app
#     merged["gemini_api_key"] = decrypt_value(merged.get("gemini_api_key_enc", ""))
#     merged["openai_api_key"] = decrypt_value(merged.get("openai_api_key_enc", ""))
#     merged["claude_api_key"] = decrypt_value(merged.get("claude_api_key_enc", ""))

#     return merged


# def save_settings(settings: dict) -> bool:
#     """
#     Accepts plain-text '*_api_key' fields, encrypts them, then writes to disk.
#     Raw API keys are NEVER persisted to disk.
#     """
#     to_save = {
#         "active_provider"    : settings.get("active_provider", "Gemini"),

#         # Encrypt each key — only save encrypted tokens
#         "gemini_api_key_enc" : encrypt_value(settings.get("gemini_api_key", "").strip()),
#         "openai_api_key_enc" : encrypt_value(settings.get("openai_api_key", "").strip()),
#         "claude_api_key_enc" : encrypt_value(settings.get("claude_api_key", "").strip()),

#         # Ollama URL (no encryption needed — it's a local URL)
#         "ollama_base_url"    : settings.get("ollama_base_url", DEFAULT_SETTINGS["ollama_base_url"]).strip(),

#         # Selected models
#         "gemini_model"       : settings.get("gemini_model", PROVIDER_CHAT_MODELS["Gemini"]),
#         "openai_model"       : settings.get("openai_model", PROVIDER_CHAT_MODELS["OpenAI"]),
#         "claude_model"       : settings.get("claude_model", PROVIDER_CHAT_MODELS["Claude"]),
#         "ollama_model"       : settings.get("ollama_model", PROVIDER_CHAT_MODELS["Ollama"]),

#         # App paths
#         "database_url"       : settings.get("database_url", DEFAULT_SETTINGS["database_url"]).strip(),
#         "export_dir"         : settings.get("export_dir", str(EXPORT_DIR)).strip(),
#     }
#     try:
#         with open(SETTINGS_PATH, "w") as f:
#             json.dump(to_save, f, indent=4)
#         print("[INFO] Settings saved (all API keys encrypted).")
#         return True
#     except Exception as e:
#         print(f"[ERROR] Failed to save settings: {e}")
#         return False


# def get_active_api_key() -> str:
#     """Returns the decrypted API key for the currently active provider."""
#     provider = ACTIVE_PROVIDER
#     if provider == "Gemini":
#         return GEMINI_API_KEY
#     elif provider == "OpenAI":
#         return OPENAI_API_KEY
#     elif provider == "Claude":
#         return CLAUDE_API_KEY
#     elif provider == "Ollama":
#         return ""   # Ollama is local — no key needed
#     return ""


# def get_active_chat_model() -> str:
#     """Returns the selected chat model for the currently active provider."""
#     provider = ACTIVE_PROVIDER
#     key_map  = {
#         "Gemini": "gemini_model",
#         "OpenAI": "openai_model",
#         "Claude": "claude_model",
#         "Ollama": "ollama_model",
#     }
#     return current_settings.get(key_map.get(provider, "gemini_model"),
#                                  PROVIDER_CHAT_MODELS.get(provider, "gemini-2.5-flash"))


# # ── Runtime Globals (used across the entire app) ───────────────────────────

# current_settings = load_settings()

# ACTIVE_PROVIDER  = current_settings.get("active_provider", "Gemini")
# GEMINI_API_KEY   = current_settings.get("gemini_api_key", "")
# OPENAI_API_KEY   = current_settings.get("openai_api_key", "")
# CLAUDE_API_KEY   = current_settings.get("claude_api_key", "")
# OLLAMA_BASE_URL  = current_settings.get("ollama_base_url", "http://localhost:11434")
# DATABASE_URL     = current_settings.get("database_url")
# EXPORT_DIR       = Path(current_settings.get("export_dir"))

# # Legacy alias so existing code that references config.GEMINI_API_KEY keeps working
# GEMINI_API_KEY   = current_settings.get("gemini_api_key", "")

# print(f"[INFO] Workspace   : {APP_DIR}")
# print(f"[INFO] Database    : {DATABASE_URL}")
# print(f"[INFO] Provider    : {ACTIVE_PROVIDER}")
# print(f"[INFO] API Key     : {'✓  (set)' if get_active_api_key() or ACTIVE_PROVIDER == 'Ollama' else '✗  (not set — go to Settings)'}")

# Version 4

# # config.py
# import os
# import json
# from pathlib import Path
# from cryptography.fernet import Fernet

# # ── Workspace Paths ────────────────────────────────────────────────────────
# APP_DIR       = Path(os.getenv("APPDATA", Path.home())) / "DocIntelTool"
# APP_DIR.mkdir(parents=True, exist_ok=True)

# DB_PATH       = APP_DIR / "app_data.db"
# CHROMA_DIR    = str(APP_DIR / "vector_store")
# EXPORT_DIR    = APP_DIR / "exports"
# SETTINGS_PATH = APP_DIR / "settings.json"
# KEY_PATH      = APP_DIR / ".secret.key"  # Machine-local only — NEVER commit this

# EXPORT_DIR.mkdir(exist_ok=True)

# # ── Supported AI Providers ─────────────────────────────────────────────────
# SUPPORTED_PROVIDERS = ["Gemini", "OpenAI", "Claude", "Ollama"]

# PROVIDER_EMBEDDING_MODELS = {
#     "Gemini": "models/embedding-001",
#     "OpenAI": "text-embedding-3-small",
#     "Claude": "text-embedding-3-small",  # Claude has no embeddings — falls back to OpenAI
#     "Ollama": "nomic-embed-text",
# }

# PROVIDER_CHAT_MODELS = {
#     "Gemini": "gemini-2.5-flash",
#     "OpenAI": "gpt-4o",
#     "Claude": "claude-sonnet-4-6",
#     "Ollama": "llama3",
# }

# # ── Encryption Helpers ─────────────────────────────────────────────────────

# def _load_or_create_fernet_key() -> Fernet:
#     """
#     Loads or generates the machine-local Fernet symmetric encryption key.
#     This key lives ONLY in AppData — never in source code or git.
#     """
#     if KEY_PATH.exists():
#         key = KEY_PATH.read_bytes()
#     else:
#         key = Fernet.generate_key()
#         KEY_PATH.write_bytes(key)
#         try:
#             os.chmod(KEY_PATH, 0o600)
#         except Exception:
#             pass
#         print(f"[INFO] Encryption key generated at: {KEY_PATH}")
#     return Fernet(key)


# _fernet = _load_or_create_fernet_key()


# def encrypt_value(plain_text: str) -> str:
#     """Encrypts a plain-text string → Fernet token string."""
#     if not plain_text:
#         return ""
#     return _fernet.encrypt(plain_text.encode()).decode()


# def decrypt_value(token: str) -> str:
#     """Decrypts a Fernet token → plain text. Returns '' on any failure."""
#     if not token:
#         return ""
#     try:
#         return _fernet.decrypt(token.encode()).decode()
#     except Exception:
#         print("[WARNING] Decryption failed — token may be from a different key.")
#         return ""


# # ── Default Settings (zero hardcoded keys) ────────────────────────────────

# db_abs_path = os.path.abspath(DB_PATH).replace("\\", "/")

# DEFAULT_SETTINGS = {
#     "active_provider"    : "Gemini",
#     "gemini_api_key_enc" : "",
#     "openai_api_key_enc" : "",
#     "claude_api_key_enc" : "",
#     "ollama_base_url"    : "http://localhost:11434",
#     "gemini_model"       : PROVIDER_CHAT_MODELS["Gemini"],
#     "openai_model"       : PROVIDER_CHAT_MODELS["OpenAI"],
#     "claude_model"       : PROVIDER_CHAT_MODELS["Claude"],
#     "ollama_model"       : PROVIDER_CHAT_MODELS["Ollama"],
#     "database_url"       : f"sqlite:///{db_abs_path}",
#     "export_dir"         : str(EXPORT_DIR),
# }


# # ── Environment Variable Injector ──────────────────────────────────────────

# def _inject_env_vars(gemini_key: str, openai_key: str, claude_key: str,
#                      ollama_url: str):
#     """
#     THE CORE FIX:
#     Pushes all decrypted API keys directly into os.environ so that every
#     LangChain / Google / OpenAI / Anthropic library finds them automatically.
#     No user needs to touch system environment variables ever.
#     Called on startup AND after every save/apply action.
#     """
#     # Gemini / Google
#     if gemini_key:
#         os.environ["GOOGLE_API_KEY"]  = gemini_key
#         os.environ["GEMINI_API_KEY"]  = gemini_key

#     # OpenAI
#     if openai_key:
#         os.environ["OPENAI_API_KEY"]  = openai_key

#     # Anthropic / Claude
#     if claude_key:
#         os.environ["ANTHROPIC_API_KEY"] = claude_key

#     # Ollama (no key — just ensure base URL is accessible if needed)
#     if ollama_url:
#         os.environ["OLLAMA_HOST"] = ollama_url

#     print(f"[INFO] ENV injected → "
#           f"Gemini={'✓' if gemini_key else '✗'}  "
#           f"OpenAI={'✓' if openai_key else '✗'}  "
#           f"Claude={'✓' if claude_key else '✗'}  "
#           f"Ollama={ollama_url}")


# # ── Settings I/O ───────────────────────────────────────────────────────────

# def load_settings() -> dict:
#     """
#     Loads settings.json, decrypts all keys, injects them into os.environ,
#     and returns the merged dict with plain-text key fields ready to use.
#     """
#     if SETTINGS_PATH.exists():
#         try:
#             with open(SETTINGS_PATH, "r") as f:
#                 saved = json.load(f)
#             merged = {**DEFAULT_SETTINGS, **saved}
#         except Exception:
#             merged = DEFAULT_SETTINGS.copy()
#     else:
#         merged = DEFAULT_SETTINGS.copy()

#     # Decrypt keys
#     merged["gemini_api_key"] = decrypt_value(merged.get("gemini_api_key_enc", ""))
#     merged["openai_api_key"] = decrypt_value(merged.get("openai_api_key_enc", ""))
#     merged["claude_api_key"] = decrypt_value(merged.get("claude_api_key_enc", ""))

#     # ── Inject into environment immediately ───────────────────────────────
#     _inject_env_vars(
#         gemini_key  = merged["gemini_api_key"],
#         openai_key  = merged["openai_api_key"],
#         claude_key  = merged["claude_api_key"],
#         ollama_url  = merged.get("ollama_base_url", "http://localhost:11434"),
#     )

#     return merged


# def save_settings(settings: dict) -> bool:
#     """
#     Encrypts all plain-text API keys and writes to disk.
#     Then immediately re-injects updated keys into os.environ.
#     Raw keys are NEVER written to disk.
#     """
#     # Resolve keys — if user left a field blank, preserve the existing encrypted value
#     existing = load_settings()

#     def _resolve(new_val: str, existing_plain: str) -> str:
#         """Use new value if provided, otherwise fall back to existing."""
#         return new_val.strip() if new_val.strip() else existing_plain

#     gemini_key = _resolve(settings.get("gemini_api_key", ""), existing.get("gemini_api_key", ""))
#     openai_key = _resolve(settings.get("openai_api_key", ""), existing.get("openai_api_key", ""))
#     claude_key = _resolve(settings.get("claude_api_key", ""), existing.get("claude_api_key", ""))

#     to_save = {
#         "active_provider"    : settings.get("active_provider", "Gemini"),
#         "gemini_api_key_enc" : encrypt_value(gemini_key),
#         "openai_api_key_enc" : encrypt_value(openai_key),
#         "claude_api_key_enc" : encrypt_value(claude_key),
#         "ollama_base_url"    : settings.get("ollama_base_url",
#                                              DEFAULT_SETTINGS["ollama_base_url"]).strip(),
#         "gemini_model"       : settings.get("gemini_model", PROVIDER_CHAT_MODELS["Gemini"]),
#         "openai_model"       : settings.get("openai_model", PROVIDER_CHAT_MODELS["OpenAI"]),
#         "claude_model"       : settings.get("claude_model", PROVIDER_CHAT_MODELS["Claude"]),
#         "ollama_model"       : settings.get("ollama_model", PROVIDER_CHAT_MODELS["Ollama"]),
#         "database_url"       : settings.get("database_url",
#                                              DEFAULT_SETTINGS["database_url"]).strip(),
#         "export_dir"         : settings.get("export_dir", str(EXPORT_DIR)).strip(),
#     }

#     try:
#         with open(SETTINGS_PATH, "w") as f:
#             json.dump(to_save, f, indent=4)
#         print("[INFO] Settings saved (keys encrypted).")
#     except Exception as e:
#         print(f"[ERROR] Failed to save settings: {e}")
#         return False

#     # ── Re-inject updated keys into os.environ immediately ────────────────
#     _inject_env_vars(
#         gemini_key = gemini_key,
#         openai_key = openai_key,
#         claude_key = claude_key,
#         ollama_url = to_save["ollama_base_url"],
#     )

#     # ── Refresh module-level globals so rest of app picks up new values ───
#     global ACTIVE_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY
#     global OLLAMA_BASE_URL, DATABASE_URL, EXPORT_DIR, current_settings

#     ACTIVE_PROVIDER = to_save["active_provider"]
#     GEMINI_API_KEY  = gemini_key
#     OPENAI_API_KEY  = openai_key
#     CLAUDE_API_KEY  = claude_key
#     OLLAMA_BASE_URL = to_save["ollama_base_url"]
#     DATABASE_URL    = to_save["database_url"]
#     EXPORT_DIR      = Path(to_save["export_dir"])
#     current_settings = {**to_save,
#                         "gemini_api_key": gemini_key,
#                         "openai_api_key": openai_key,
#                         "claude_api_key": claude_key}

#     return True


# # ── Convenience Getters ────────────────────────────────────────────────────

# def get_active_api_key() -> str:
#     """Returns the plain-text API key for the currently active provider."""
#     return {
#         "Gemini": GEMINI_API_KEY,
#         "OpenAI": OPENAI_API_KEY,
#         "Claude": CLAUDE_API_KEY,
#         "Ollama": "",
#     }.get(ACTIVE_PROVIDER, "")


# def get_active_chat_model() -> str:
#     """Returns the selected chat model name for the active provider."""
#     key_map = {
#         "Gemini": "gemini_model",
#         "OpenAI": "openai_model",
#         "Claude": "claude_model",
#         "Ollama": "ollama_model",
#     }
#     return current_settings.get(
#         key_map.get(ACTIVE_PROVIDER, "gemini_model"),
#         PROVIDER_CHAT_MODELS.get(ACTIVE_PROVIDER, "gemini-2.5-flash")
#     )


# # ── Bootstrap — runs once when the module is first imported ───────────────

# current_settings = load_settings()   # also calls _inject_env_vars internally

# ACTIVE_PROVIDER  = current_settings.get("active_provider", "Gemini")
# GEMINI_API_KEY   = current_settings.get("gemini_api_key", "")
# OPENAI_API_KEY   = current_settings.get("openai_api_key", "")
# CLAUDE_API_KEY   = current_settings.get("claude_api_key", "")
# OLLAMA_BASE_URL  = current_settings.get("ollama_base_url", "http://localhost:11434")
# DATABASE_URL     = current_settings.get("database_url")
# EXPORT_DIR       = Path(current_settings.get("export_dir"))

# print(f"[INFO] Workspace : {APP_DIR}")
# print(f"[INFO] Database  : {DATABASE_URL}")
# print(f"[INFO] Provider  : {ACTIVE_PROVIDER}")
# print(f"[INFO] API Key   : "
#       f"{'✓ ready' if get_active_api_key() or ACTIVE_PROVIDER == 'Ollama' else '✗ not set — open Settings'}")

# Version 5

# config.py
# import os
# import json
# from pathlib import Path
# from cryptography.fernet import Fernet

# # ── Workspace Paths ────────────────────────────────────────────────────────
# APP_DIR       = Path(os.getenv("APPDATA", Path.home())) / "DocIntelTool"
# APP_DIR.mkdir(parents=True, exist_ok=True)

# DB_PATH       = APP_DIR / "app_data.db"
# CHROMA_DIR    = str(APP_DIR / "vector_store")
# EXPORT_DIR    = APP_DIR / "exports"
# SETTINGS_PATH = APP_DIR / "settings.json"
# KEY_PATH      = APP_DIR / ".secret.key"  # Machine-local only — NEVER commit this

# EXPORT_DIR.mkdir(exist_ok=True)

# # ── Supported AI Providers ─────────────────────────────────────────────────
# SUPPORTED_PROVIDERS = ["Gemini", "OpenAI", "Claude", "Ollama"]

# PROVIDER_EMBEDDING_MODELS = {
#     "Gemini": "models/embedding-001",
#     "OpenAI": "text-embedding-3-small",
#     "Claude": "text-embedding-3-small",  # Claude has no embeddings — falls back to OpenAI
#     "Ollama": "nomic-embed-text",
# }

# PROVIDER_CHAT_MODELS = {
#     "Gemini": "gemini-2.5-flash",
#     "OpenAI": "gpt-4o",
#     "Claude": "claude-sonnet-4-6",
#     "Ollama": "llama3",
# }

# # ── Encryption Helpers ─────────────────────────────────────────────────────

# def _load_or_create_fernet_key() -> Fernet:
#     """
#     Loads or generates the machine-local Fernet symmetric encryption key.
#     This key lives ONLY in AppData — never in source code or git.
#     """
#     if KEY_PATH.exists():
#         key = KEY_PATH.read_bytes()
#     else:
#         key = Fernet.generate_key()
#         KEY_PATH.write_bytes(key)
#         try:
#             os.chmod(KEY_PATH, 0o600)
#         except Exception:
#             pass
#         print(f"[INFO] Encryption key generated at: {KEY_PATH}")
#     return Fernet(key)


# _fernet = _load_or_create_fernet_key()


# def encrypt_value(plain_text: str) -> str:
#     """Encrypts a plain-text string → Fernet token string."""
#     if not plain_text:
#         return ""
#     return _fernet.encrypt(plain_text.encode()).decode()


# def decrypt_value(token: str) -> str:
#     """Decrypts a Fernet token → plain text. Returns '' on any failure."""
#     if not token:
#         return ""
#     try:
#         return _fernet.decrypt(token.encode()).decode()
#     except Exception:
#         print("[WARNING] Decryption failed — token may be from a different key.")
#         return ""


# # ── Default Settings (zero hardcoded keys) ────────────────────────────────

# db_abs_path = os.path.abspath(DB_PATH).replace("\\", "/")

# DEFAULT_SETTINGS = {
#     "active_provider"    : "Gemini",
#     "gemini_api_key_enc" : "",
#     "openai_api_key_enc" : "",
#     "claude_api_key_enc" : "",
#     "ollama_base_url"    : "http://localhost:11434",
#     "gemini_model"       : PROVIDER_CHAT_MODELS["Gemini"],
#     "openai_model"       : PROVIDER_CHAT_MODELS["OpenAI"],
#     "claude_model"       : PROVIDER_CHAT_MODELS["Claude"],
#     "ollama_model"       : PROVIDER_CHAT_MODELS["Ollama"],
#     "database_url"       : f"sqlite:///{db_abs_path}",
#     "export_dir"         : str(EXPORT_DIR),
# }


# # ── Environment Variable Injector ──────────────────────────────────────────

# def _inject_env_vars(gemini_key: str, openai_key: str, claude_key: str,
#                      ollama_url: str):
#     """
#     THE CORE FIX:
#     Pushes all decrypted API keys directly into os.environ so that every
#     LangChain / Google / OpenAI / Anthropic library finds them automatically.
#     No user needs to touch system environment variables ever.
#     Called on startup AND after every save/apply action.
#     """
#     # Gemini / Google
#     if gemini_key:
#         os.environ["GOOGLE_API_KEY"]  = gemini_key
#         os.environ["GEMINI_API_KEY"]  = gemini_key

#     # OpenAI
#     if openai_key:
#         os.environ["OPENAI_API_KEY"]  = openai_key

#     # Anthropic / Claude
#     if claude_key:
#         os.environ["ANTHROPIC_API_KEY"] = claude_key

#     # Ollama (no key — just ensure base URL is accessible if needed)
#     if ollama_url:
#         os.environ["OLLAMA_HOST"] = ollama_url

#     print(f"[INFO] ENV injected → "
#           f"Gemini={'✓' if gemini_key else '✗'}  "
#           f"OpenAI={'✓' if openai_key else '✗'}  "
#           f"Claude={'✓' if claude_key else '✗'}  "
#           f"Ollama={ollama_url}")


# # ── Settings I/O ───────────────────────────────────────────────────────────

# def load_settings() -> dict:
#     """
#     Loads settings.json, decrypts all keys, injects them into os.environ,
#     and returns the merged dict with plain-text key fields ready to use.
#     """
#     if SETTINGS_PATH.exists():
#         try:
#             with open(SETTINGS_PATH, "r") as f:
#                 saved = json.load(f)
#             merged = {**DEFAULT_SETTINGS, **saved}
#         except Exception:
#             merged = DEFAULT_SETTINGS.copy()
#     else:
#         merged = DEFAULT_SETTINGS.copy()

#     # Decrypt keys
#     merged["gemini_api_key"] = decrypt_value(merged.get("gemini_api_key_enc", ""))
#     merged["openai_api_key"] = decrypt_value(merged.get("openai_api_key_enc", ""))
#     merged["claude_api_key"] = decrypt_value(merged.get("claude_api_key_enc", ""))

#     # ── Inject into environment immediately ───────────────────────────────
#     _inject_env_vars(
#         gemini_key  = merged["gemini_api_key"],
#         openai_key  = merged["openai_api_key"],
#         claude_key  = merged["claude_api_key"],
#         ollama_url  = merged.get("ollama_base_url", "http://localhost:11434"),
#     )

#     return merged


# def save_settings(settings: dict) -> bool:
#     """
#     Encrypts all plain-text API keys and writes to disk.
#     Then immediately re-injects updated keys into os.environ.
#     Raw keys are NEVER written to disk.
#     """
#     # ── Declare globals FIRST — Python requires this before any use ───────
#     global ACTIVE_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY
#     global OLLAMA_BASE_URL, DATABASE_URL, EXPORT_DIR, current_settings

#     # Resolve keys — if user left a field blank, preserve the existing encrypted value
#     existing = load_settings()

#     def _resolve(new_val: str, existing_plain: str) -> str:
#         """Use new value if provided, otherwise fall back to existing."""
#         return new_val.strip() if new_val.strip() else existing_plain

#     gemini_key = _resolve(settings.get("gemini_api_key", ""), existing.get("gemini_api_key", ""))
#     openai_key = _resolve(settings.get("openai_api_key", ""), existing.get("openai_api_key", ""))
#     claude_key = _resolve(settings.get("claude_api_key", ""), existing.get("claude_api_key", ""))

#     to_save = {
#         "active_provider"    : settings.get("active_provider", "Gemini"),
#         "gemini_api_key_enc" : encrypt_value(gemini_key),
#         "openai_api_key_enc" : encrypt_value(openai_key),
#         "claude_api_key_enc" : encrypt_value(claude_key),
#         "ollama_base_url"    : settings.get("ollama_base_url",
#                                              DEFAULT_SETTINGS["ollama_base_url"]).strip(),
#         "gemini_model"       : settings.get("gemini_model", PROVIDER_CHAT_MODELS["Gemini"]),
#         "openai_model"       : settings.get("openai_model", PROVIDER_CHAT_MODELS["OpenAI"]),
#         "claude_model"       : settings.get("claude_model", PROVIDER_CHAT_MODELS["Claude"]),
#         "ollama_model"       : settings.get("ollama_model", PROVIDER_CHAT_MODELS["Ollama"]),
#         "database_url"       : settings.get("database_url",
#                                              DEFAULT_SETTINGS["database_url"]).strip(),
#         "export_dir"         : settings.get("export_dir", str(EXPORT_DIR)).strip(),
#     }

#     try:
#         with open(SETTINGS_PATH, "w") as f:
#             json.dump(to_save, f, indent=4)
#         print("[INFO] Settings saved (keys encrypted).")
#     except Exception as e:
#         print(f"[ERROR] Failed to save settings: {e}")
#         return False

#     # ── Re-inject updated keys into os.environ immediately ────────────────
#     _inject_env_vars(
#         gemini_key = gemini_key,
#         openai_key = openai_key,
#         claude_key = claude_key,
#         ollama_url = to_save["ollama_base_url"],
#     )

#     # ── Refresh module-level globals so rest of app picks up new values ───
#     ACTIVE_PROVIDER = to_save["active_provider"]
#     GEMINI_API_KEY  = gemini_key
#     OPENAI_API_KEY  = openai_key
#     CLAUDE_API_KEY  = claude_key
#     OLLAMA_BASE_URL = to_save["ollama_base_url"]
#     DATABASE_URL    = to_save["database_url"]
#     EXPORT_DIR      = Path(to_save["export_dir"])
#     current_settings = {**to_save,
#                         "gemini_api_key": gemini_key,
#                         "openai_api_key": openai_key,
#                         "claude_api_key": claude_key}

#     return True


# # ── Convenience Getters ────────────────────────────────────────────────────

# def get_active_api_key() -> str:
#     """Returns the plain-text API key for the currently active provider."""
#     return {
#         "Gemini": GEMINI_API_KEY,
#         "OpenAI": OPENAI_API_KEY,
#         "Claude": CLAUDE_API_KEY,
#         "Ollama": "",
#     }.get(ACTIVE_PROVIDER, "")


# def get_active_chat_model() -> str:
#     """Returns the selected chat model name for the active provider."""
#     key_map = {
#         "Gemini": "gemini_model",
#         "OpenAI": "openai_model",
#         "Claude": "claude_model",
#         "Ollama": "ollama_model",
#     }
#     return current_settings.get(
#         key_map.get(ACTIVE_PROVIDER, "gemini_model"),
#         PROVIDER_CHAT_MODELS.get(ACTIVE_PROVIDER, "gemini-2.5-flash")
#     )


# # ── Bootstrap — runs once when the module is first imported ───────────────

# current_settings = load_settings()   # also calls _inject_env_vars internally

# ACTIVE_PROVIDER  = current_settings.get("active_provider", "Gemini")
# GEMINI_API_KEY   = current_settings.get("gemini_api_key", "")
# OPENAI_API_KEY   = current_settings.get("openai_api_key", "")
# CLAUDE_API_KEY   = current_settings.get("claude_api_key", "")
# OLLAMA_BASE_URL  = current_settings.get("ollama_base_url", "http://localhost:11434")
# DATABASE_URL     = current_settings.get("database_url")
# EXPORT_DIR       = Path(current_settings.get("export_dir"))

# print(f"[INFO] Workspace : {APP_DIR}")
# print(f"[INFO] Database  : {DATABASE_URL}")
# print(f"[INFO] Provider  : {ACTIVE_PROVIDER}")
# print(f"[INFO] API Key   : "
#       f"{'✓ ready' if get_active_api_key() or ACTIVE_PROVIDER == 'Ollama' else '✗ not set — open Settings'}")

# Version 56
# config.py

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet

# ── Workspace Paths ────────────────────────────────────────────────────────
APP_DIR       = Path(os.getenv("APPDATA", Path.home())) / "DocIntelTool"
APP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH       = APP_DIR / "app_data.db"
CHROMA_DIR    = str(APP_DIR / "vector_store")
EXPORT_DIR    = APP_DIR / "exports"
SETTINGS_PATH = APP_DIR / "settings.json"
KEY_PATH      = APP_DIR / ".secret.key"  # Machine-local only — NEVER commit this

EXPORT_DIR.mkdir(exist_ok=True)

# ── Supported AI Providers ─────────────────────────────────────────────────
SUPPORTED_PROVIDERS = ["Gemini", "OpenAI", "Claude", "Ollama"]

PROVIDER_EMBEDDING_MODELS = {
    "Gemini": "models/text-embedding-004",
    "OpenAI": "text-embedding-3-small",
    "Claude": "text-embedding-3-small",  # Claude has no embeddings — falls back to OpenAI
    "Ollama": "nomic-embed-text",
}

PROVIDER_CHAT_MODELS = {
    "Gemini": "gemini-2.5-flash",
    "OpenAI": "gpt-4o",
    "Claude": "claude-sonnet-4-6",
    "Ollama": "llama3",
}

# ── Encryption Helpers ─────────────────────────────────────────────────────

def _load_or_create_fernet_key() -> Fernet:
    """
    Loads or generates the machine-local Fernet symmetric encryption key.
    This key lives ONLY in AppData — never in source code or git.
    """
    if KEY_PATH.exists():
        key = KEY_PATH.read_bytes()
    else:
        key = Fernet.generate_key()
        KEY_PATH.write_bytes(key)
        try:
            os.chmod(KEY_PATH, 0o600)
        except Exception:
            pass
        print(f"[INFO] Encryption key generated at: {KEY_PATH}")
    return Fernet(key)


_fernet = _load_or_create_fernet_key()


def encrypt_value(plain_text: str) -> str:
    """Encrypts a plain-text string → Fernet token string."""
    if not plain_text:
        return ""
    return _fernet.encrypt(plain_text.encode()).decode()


def decrypt_value(token: str) -> str:
    """Decrypts a Fernet token → plain text. Returns '' on any failure."""
    if not token:
        return ""
    try:
        return _fernet.decrypt(token.encode()).decode()
    except Exception:
        print("[WARNING] Decryption failed — token may be from a different key.")
        return ""


# ── Default Settings (zero hardcoded keys) ────────────────────────────────

db_abs_path = os.path.abspath(DB_PATH).replace("\\", "/")

DEFAULT_SETTINGS = {
    "active_provider"    : "Gemini",
    "gemini_api_key_enc" : "",
    "openai_api_key_enc" : "",
    "claude_api_key_enc" : "",
    "ollama_base_url"    : "http://localhost:11434",
    "gemini_model"       : PROVIDER_CHAT_MODELS["Gemini"],
    "openai_model"       : PROVIDER_CHAT_MODELS["OpenAI"],
    "claude_model"       : PROVIDER_CHAT_MODELS["Claude"],
    "ollama_model"       : PROVIDER_CHAT_MODELS["Ollama"],
    "database_url"       : f"sqlite:///{db_abs_path}",
    "export_dir"         : str(EXPORT_DIR),
}


# ── Environment Variable Injector ──────────────────────────────────────────

def _inject_env_vars(gemini_key: str, openai_key: str, claude_key: str,
                     ollama_url: str):
    """
    THE CORE FIX:
    Pushes all decrypted API keys directly into os.environ so that every
    LangChain / Google / OpenAI / Anthropic library finds them automatically.
    No user needs to touch system environment variables ever.
    Called on startup AND after every save/apply action.
    """
    # Gemini / Google
    if gemini_key:
        os.environ["GOOGLE_API_KEY"]  = gemini_key
        os.environ["GEMINI_API_KEY"]  = gemini_key

    # OpenAI
    if openai_key:
        os.environ["OPENAI_API_KEY"]  = openai_key

    # Anthropic / Claude
    if claude_key:
        os.environ["ANTHROPIC_API_KEY"] = claude_key

    # Ollama (no key — just ensure base URL is accessible if needed)
    if ollama_url:
        os.environ["OLLAMA_HOST"] = ollama_url

    print(f"[INFO] ENV injected → "
          f"Gemini={'✓' if gemini_key else '✗'}  "
          f"OpenAI={'✓' if openai_key else '✗'}  "
          f"Claude={'✓' if claude_key else '✗'}  "
          f"Ollama={ollama_url}")


# ── Settings I/O ───────────────────────────────────────────────────────────

def load_settings() -> dict:
    """
    Loads settings.json, decrypts all keys, injects them into os.environ,
    and returns the merged dict with plain-text key fields ready to use.
    """
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r") as f:
                saved = json.load(f)
            merged = {**DEFAULT_SETTINGS, **saved}
        except Exception:
            merged = DEFAULT_SETTINGS.copy()
    else:
        merged = DEFAULT_SETTINGS.copy()

    # Decrypt keys
    merged["gemini_api_key"] = decrypt_value(merged.get("gemini_api_key_enc", ""))
    merged["openai_api_key"] = decrypt_value(merged.get("openai_api_key_enc", ""))
    merged["claude_api_key"] = decrypt_value(merged.get("claude_api_key_enc", ""))

    # ── Inject into environment immediately ───────────────────────────────
    _inject_env_vars(
        gemini_key  = merged["gemini_api_key"],
        openai_key  = merged["openai_api_key"],
        claude_key  = merged["claude_api_key"],
        ollama_url  = merged.get("ollama_base_url", "http://localhost:11434"),
    )

    return merged


def save_settings(settings: dict) -> bool:
    """
    Encrypts all plain-text API keys and writes to disk.
    Then immediately re-injects updated keys into os.environ.
    Raw keys are NEVER written to disk.
    """
    # ── Declare globals FIRST — Python requires this before any use ───────
    global ACTIVE_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY
    global OLLAMA_BASE_URL, DATABASE_URL, EXPORT_DIR, current_settings

    # Resolve keys — if user left a field blank, preserve the existing encrypted value
    existing = load_settings()

    def _resolve(new_val: str, existing_plain: str) -> str:
        """Use new value if provided, otherwise fall back to existing."""
        return new_val.strip() if new_val.strip() else existing_plain

    gemini_key = _resolve(settings.get("gemini_api_key", ""), existing.get("gemini_api_key", ""))
    openai_key = _resolve(settings.get("openai_api_key", ""), existing.get("openai_api_key", ""))
    claude_key = _resolve(settings.get("claude_api_key", ""), existing.get("claude_api_key", ""))

    to_save = {
        "active_provider"    : settings.get("active_provider", "Gemini"),
        "gemini_api_key_enc" : encrypt_value(gemini_key),
        "openai_api_key_enc" : encrypt_value(openai_key),
        "claude_api_key_enc" : encrypt_value(claude_key),
        "ollama_base_url"    : settings.get("ollama_base_url",
                                             DEFAULT_SETTINGS["ollama_base_url"]).strip(),
        "gemini_model"       : settings.get("gemini_model", PROVIDER_CHAT_MODELS["Gemini"]),
        "openai_model"       : settings.get("openai_model", PROVIDER_CHAT_MODELS["OpenAI"]),
        "claude_model"       : settings.get("claude_model", PROVIDER_CHAT_MODELS["Claude"]),
        "ollama_model"       : settings.get("ollama_model", PROVIDER_CHAT_MODELS["Ollama"]),
        "database_url"       : settings.get("database_url",
                                             DEFAULT_SETTINGS["database_url"]).strip(),
        "export_dir"         : settings.get("export_dir", str(EXPORT_DIR)).strip(),
    }

    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(to_save, f, indent=4)
        print("[INFO] Settings saved (keys encrypted).")
    except Exception as e:
        print(f"[ERROR] Failed to save settings: {e}")
        return False

    # ── Re-inject updated keys into os.environ immediately ────────────────
    _inject_env_vars(
        gemini_key = gemini_key,
        openai_key = openai_key,
        claude_key = claude_key,
        ollama_url = to_save["ollama_base_url"],
    )

    # ── Refresh module-level globals so rest of app picks up new values ───
    ACTIVE_PROVIDER = to_save["active_provider"]
    GEMINI_API_KEY  = gemini_key
    OPENAI_API_KEY  = openai_key
    CLAUDE_API_KEY  = claude_key
    OLLAMA_BASE_URL = to_save["ollama_base_url"]
    DATABASE_URL    = to_save["database_url"]
    EXPORT_DIR      = Path(to_save["export_dir"])
    current_settings = {**to_save,
                        "gemini_api_key": gemini_key,
                        "openai_api_key": openai_key,
                        "claude_api_key": claude_key}

    return True


# ── Convenience Getters ────────────────────────────────────────────────────

def get_active_api_key() -> str:
    """Returns the plain-text API key for the currently active provider."""
    return {
        "Gemini": GEMINI_API_KEY,
        "OpenAI": OPENAI_API_KEY,
        "Claude": CLAUDE_API_KEY,
        "Ollama": "",
    }.get(ACTIVE_PROVIDER, "")


def get_active_chat_model() -> str:
    """Returns the selected chat model name for the active provider."""
    key_map = {
        "Gemini": "gemini_model",
        "OpenAI": "openai_model",
        "Claude": "claude_model",
        "Ollama": "ollama_model",
    }
    return current_settings.get(
        key_map.get(ACTIVE_PROVIDER, "gemini_model"),
        PROVIDER_CHAT_MODELS.get(ACTIVE_PROVIDER, "gemini-2.5-flash")
    )


# ── Bootstrap — runs once when the module is first imported ───────────────

current_settings = load_settings()   # also calls _inject_env_vars internally

ACTIVE_PROVIDER  = current_settings.get("active_provider", "Gemini")
GEMINI_API_KEY   = current_settings.get("gemini_api_key", "")
OPENAI_API_KEY   = current_settings.get("openai_api_key", "")
CLAUDE_API_KEY   = current_settings.get("claude_api_key", "")
OLLAMA_BASE_URL  = current_settings.get("ollama_base_url", "http://localhost:11434")
DATABASE_URL     = current_settings.get("database_url")
EXPORT_DIR       = Path(current_settings.get("export_dir"))

print(f"[INFO] Workspace : {APP_DIR}")
print(f"[INFO] Database  : {DATABASE_URL}")
print(f"[INFO] Provider  : {ACTIVE_PROVIDER}")
print(f"[INFO] API Key   : "
      f"{'✓ ready' if get_active_api_key() or ACTIVE_PROVIDER == 'Ollama' else '✗ not set — open Settings'}")
