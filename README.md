# 🧠 DocuMind AI — Intelligent Document Assistant

> **Local AI-powered desktop application to chat with documents and extract structured data — supporting Gemini, OpenAI, Claude, and Ollama with encrypted API key management.**

---

## 📌 Description

DocuMind AI is a production-ready desktop application that transforms how you interact with documents. Upload any file — PDF, Word, Excel, CSV, or plain text — and either **converse with it naturally using RAG-powered Q&A with page-level citations**, or **run an autonomous LangGraph agent pipeline** that discovers the document's schema, extracts structured records, self-heals validation errors, and upserts clean data into a database with an Excel export.

All API keys are **encrypted at rest using AES-128 Fernet** and injected into the runtime environment automatically — no manual system environment variable setup required.

---

## ✨ Features

- 💬 **Document Q&A** — RAG-powered chat with page-level citations across PDF, DOCX, TXT, CSV, XLSX
- 🤖 **Agentic Data Extraction** — Self-healing LangGraph pipeline: schema discovery → extraction → validation → upsert
- 🔀 **Multi-Provider AI** — Switch between Google Gemini, OpenAI, Anthropic Claude, and Ollama (local LLM)
- 🔒 **Encrypted Key Management** — AES-128 Fernet encryption; paste key → Apply Now → live instantly, no restart
- 🗄️ **Dynamic Database Upsert** — Auto-creates SQLAlchemy tables and performs differential insert/update operations
- 📊 **Excel Export** — Auto-formatted workbook generated after every extraction run
- 📁 **Multi-Format Support** — PDF, DOCX, TXT, CSV, XLSX/XLS, and direct SQLite/MySQL database connections
- 🧩 **Session Management** — Isolated per-document chat sessions with persistent SQLite message history
- 🖥️ **Polished Dark UI** — Modern native desktop experience built with CustomTkinter

---

## 🏗️ Architecture Overview

```
DocuMind AI
├── ui/
│   ├── main.py              # App entry point & two-pane layout
│   ├── sidebar.py           # Session management & file upload
│   ├── chat_window.py       # Chat interface per document session
│   └── settings_dialog.py  # Multi-provider key management & settings
│
├── core/
│   ├── rag_engine.py        # Multi-provider RAG: embeddings, ChromaDB, LLM Q&A
│   ├── agent_flow.py        # LangGraph agentic extraction pipeline
│   └── parser.py            # Multi-format document parser
│
├── storage/
│   ├── database.py          # SQLite session & message store
│   ├── db_ops.py            # Dynamic SQLAlchemy table ops & audit logs
│   └── exporter.py          # Excel & SQL export utilities
│
├── config.py                # Encrypted settings — Fernet key management & env injection
└── build_app.py             # PyInstaller packaging script
```

---

## 🤖 AI Agent Pipeline

Every uploaded document can be processed through a **self-healing LangGraph state machine**:

```
Parse File
    ↓
Discover Schema  (LLM infers column names & data types)
    ↓
Extract Records  (LLM extracts structured rows)
    ↓
Validate         (Type casting, primary key checks)
    ↓
  ┌─ Errors? ──→ Self-Heal (up to 3 LLM retries) ──┐
  │                                                   ↓
  └───────────────────────────────────────────── Upsert to DB
                                                      ↓
                                               Export to Excel
```

---

## 🔀 Multi-Provider Support

| Provider | Chat | Embeddings | Key Required |
|---|---|---|---|
| Google Gemini | ✅ `gemini-2.5-flash` | ✅ `gemini-embedding-001` | Gemini API Key |
| OpenAI | ✅ `gpt-4o` | ✅ `text-embedding-3-small` | OpenAI API Key |
| Anthropic Claude | ✅ `claude-sonnet-4-6` | ⚡ Uses OpenAI embeddings | Claude + OpenAI Key |
| Ollama (Local) | ✅ `llama3` | ✅ `nomic-embed-text` | None (local) |

---

## 📁 Supported File Types

| Format | Type | Notes |
|---|---|---|
| `.pdf` | Unstructured | Page-by-page text & table extraction via PyMuPDF |
| `.docx` | Unstructured | Paragraphs, tables & embedded images |
| `.txt` | Unstructured | Plain text |
| `.csv` | Tabular | Pandas-powered |
| `.xlsx` / `.xls` | Tabular | Multi-sheet support via openpyxl |
| SQLite / MySQL | Relational | Direct table connection via SQLAlchemy |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- API key for your preferred provider — [Gemini](https://aistudio.google.com/app/apikey) (free), [OpenAI](https://platform.openai.com/api-keys), [Anthropic](https://console.anthropic.com/), or [Ollama](https://ollama.com/) locally

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/documind-ai.git
cd documind-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

### First Launch
1. Open the app — workspace is auto-created at `%APPDATA%/DocIntelTool/`
2. Click **⚙ Settings** → select your **AI Provider** → paste your **API Key** → click **⚡ Apply Now**
3. Key is encrypted and injected into the environment instantly — no restart needed
4. Click **＋ Upload Document**, select any supported file, and start chatting!

---

## 🔒 API Key Security

- Keys encrypted with **AES-128 Fernet** symmetric encryption
- Raw keys are **never written to disk** — only encrypted tokens are stored in `settings.json`
- Machine-local encryption key stored at `%APPDATA%/DocIntelTool/.secret.key` — never committed to git
- Keys injected into `os.environ` automatically at startup and on every Apply — no manual `sysdm.cpl` setup

---

## 📦 Build Executable (Windows)

```bash
pip install pyinstaller
python build_app.py
```

Output:
```
dist/DocuMind AI/DocuMind AI.exe
```

Zip the entire `dist/DocuMind AI/` folder for distribution — zero Python dependency on end-user machines.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| LLM Providers | Google Gemini 2.5 Flash · OpenAI GPT-4o · Anthropic Claude · Ollama |
| Embeddings | `gemini-embedding-001` · `text-embedding-3-small` · `nomic-embed-text` |
| LLM Orchestration | [LangChain](https://langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/) |
| Vector Store | [ChromaDB](https://www.trychroma.com/) via `langchain-chroma` |
| PDF Parsing | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) |
| Word Parsing | [python-docx](https://python-docx.readthedocs.io/) |
| Tabular Data | [Pandas](https://pandas.pydata.org/) + [openpyxl](https://openpyxl.readthedocs.io/) |
| Database ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| Encryption | [cryptography](https://cryptography.io/) — Fernet AES-128 |
| Session Store | SQLite |
| Packaging | [PyInstaller](https://pyinstaller.org/) |

---

## ⚙️ Configuration

Settings stored at `%APPDATA%/DocIntelTool/settings.json` — all keys encrypted:

```json
{
  "active_provider": "Gemini",
  "gemini_api_key_enc": "<encrypted>",
  "openai_api_key_enc": "<encrypted>",
  "claude_api_key_enc": "<encrypted>",
  "ollama_base_url": "http://localhost:11434",
  "gemini_model": "gemini-2.5-flash",
  "database_url": "sqlite:///path/to/app_data.db",
  "export_dir": "C:/Users/You/AppData/Roaming/DocIntelTool/exports"
}
```

Manageable directly via **⚙ Settings** dialog (`Ctrl+,`) — no manual file editing needed.

---

## 📋 Requirements

```
customtkinter
langchain
langchain-core
langchain-community
langchain-text-splitters
langchain-google-genai
langchain-openai
langchain-anthropic
langchain-chroma
chromadb
langgraph
pymupdf
python-docx
pandas
openpyxl
sqlalchemy
cryptography
pydantic
pillow
```

---

## 🗺️ Roadmap

- [ ] macOS & Linux support
- [ ] Multi-document cross-session search
- [ ] OCR support for scanned PDFs
- [ ] Cloud database sync (PostgreSQL, Supabase)
- [ ] Bulk document batch processing
- [ ] Chat export to PDF / Word

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [LangChain](https://langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/) for the agent framework
- [Google Gemini](https://deepmind.google/technologies/gemini/), [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Ollama](https://ollama.com/) for AI backends
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the UI components
- [ChromaDB](https://www.trychroma.com/) for local vector storage

---

<p align="center">Built with ❤️ using Python, LangChain & Google Gemini</p>
