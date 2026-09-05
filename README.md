# BharatBot-Indian-Language-RagAgent-

# 🇮🇳 BharatBot — Multilingual Indian Language RAG Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-Latest-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Sarvam AI](https://img.shields.io/badge/Sarvam--30B-LLM-orange?style=for-the-badge)
![Azure AI Foundry](https://img.shields.io/badge/Azure_AI_Foundry-GPT--4o-blue?style=for-the-badge&logo=microsoftazure)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Upload any document. Ask anything. Get answers in your language.**

*The first open-source RAG agent built natively for India's 22 scheduled languages.*

[Live Demo](#) · [Report Bug](https://github.com/yourusername/bharatbot/issues) · [Request Feature](https://github.com/yourusername/bharatbot/issues)

</div>

---

## 🌟 What is BharatBot?

BharatBot is an **autonomous multilingual document intelligence agent** that allows anyone to upload documents in any Indian language and have natural, contextual conversations about them — in whatever language they are most comfortable with.

A farmer in Tamil Nadu can upload a government agricultural scheme PDF written in Tamil and ask questions in Tamil. A lawyer in Mumbai can upload a legal contract in English and get summaries in Hindi. A student in Hyderabad can upload Telugu study material and quiz themselves in Telugu or English.

**BharatBot breaks the language barrier in document intelligence.**

---

## ✨ Key Features

- 🗣️ **Truly Multilingual** — Supports all 22 scheduled Indian languages including Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Urdu and more
- 📄 **Any Document Format** — Upload PDF, DOCX, or TXT files in any language
- 🔄 **Auto Language Detection** — Automatically detects what language the user is writing in and responds in the same language
- 🧠 **Stateful Conversations** — Remembers context across multiple turns within a session
- 🔍 **Semantic Search** — Uses multilingual vector embeddings to find the most relevant content even when query language differs from document language (cross-lingual accuracy for lower-resource Indic language pairs is still being validated — see [Known Limitations](#-known-limitations))
- ⚡ **Language-Routed Generation** — Indic-language queries go to Sarvam-30B, English queries go to Azure GPT-4o — each model handles what it's actually best at
- 📊 **Source Attribution** — Every answer cites the exact source document it retrieved from
- 🔒 **Strictly Domain-Bound** — Refuses to answer from general knowledge when the uploaded documents don't contain the answer, and treats document content as untrusted data rather than instructions (basic prompt-injection resistance)
- 🛡️ **Scanned Document Support** — OCR fallback using Tesseract for image-based PDFs
- 🔁 **Automatic Fallback** — If the primary model for a language is unavailable, falls back to the other, then to Claude Sonnet as a last resort

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│              React + Tailwind CSS (served by nginx)          │
│         Upload Panel │ Chat Window │ Language Badges         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP REST (CORS, browser → API)
┌──────────────────────────▼──────────────────────────────────┐
│                       FASTAPI BACKEND                        │
│              /upload    /chat    /health                     │
└──────────┬───────────────────────────────┬──────────────────┘
           │                               │
┌──────────▼──────────┐      ┌─────────────▼──────────────────┐
│   INGESTION LAYER   │      │        AGENT LAYER             │
│                     │      │                                 │
│  PDF Loader         │      │  LangGraph State Machine        │
│  OCR Loader         │      │                                 │
│  Text Chunker       │      │  Node 1: detect_language        │
│  Embedder           │      │       ↓                         │
│  Vector Store       │      │  Node 2: retrieve_docs          │
│       ↓             │      │       ↓                         │
│  Postgres+pgvector  │      │  Node 3: generate_response      │
└─────────────────────┘      └──────────────┬─────────────────┘
                                            │
                             ┌──────────────▼─────────────────┐
                             │          LLM LAYER             │
                             │                                 │
                             │  Indic queries:  Sarvam-30B     │
                             │  English queries: Azure GPT-4o  │
                             │  Final fallback:  Claude Sonnet │
                             │                                 │
                             │  Embeddings:                    │
                             │  Azure OpenAI                   │
                             │  text-embedding-3-small         │
                             └────────────────────────────────┘
```

---

## 🧠 How It Works — Deep Dive

### Step 1 — Document Ingestion Pipeline

When a user uploads a document, it goes through a 4-stage pipeline:

```
Document Upload
      │
      ▼
┌─────────────┐
│  File Type  │──── PDF ────► PyMuPDF Text Extraction
│  Detection  │                      │
│             │                      ▼
│             │              Text Layer Check
│             │              (< 100 chars?)
│             │                      │
│             │              YES ────► Tesseract OCR
│             │              NO  ────► Use extracted text
│             │
│             │──── DOCX ───► python-docx paragraph extract
│             │
│             │──── TXT  ───► Direct UTF-8 read
└─────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│         Universal Text Chunker          │
│                                         │
│  RecursiveCharacterTextSplitter         │
│  chunk_size=400, overlap=50             │
│  separators=["\n\n","\n","।","."," "]  │
│                                         │
│  The Devanagari danda (।) is included  │
│  as a separator — Hindi and Marathi     │
│  documents split at natural sentence    │
│  boundaries automatically              │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│  Azure OpenAI text-embedding-3-small    │
│                                         │
│  Each chunk is sent to the Azure       │
│  embeddings deployment (batched at     │
│  100 chunks/call) and converted into   │
│  a 1536-dim vector                     │
│                                         │
│  Trained across many languages in the  │
│  SAME vector space — critical for       │
│  cross-language retrieval              │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│      Postgres + pgvector Vector Store   │
│                                         │
│  HNSW index — approximate nearest      │
│  neighbor search (vector_l2_ops)        │
│  One table: text, source, chunk_id,    │
│  embedding                             │
└─────────────────────────────────────────┘
```

### Step 2 — LangGraph Agent State Machine

Every user query flows through a deterministic 3-node LangGraph graph:

```python
BharatBotState = {
    "query": str,              # raw user input
    "query_language": str,     # auto-detected language code
    "retrieved_docs": list,    # top-k relevant chunks
    "sources": list,           # source filenames
    "response": str,           # final LLM response
    "session_id": str          # for memory persistence
}
```

```
User Query
    │
    ▼
┌───────────────────────────────┐
│   Node 1: detect_language     │
│                               │
│   Uses lingua-py library      │
│   Detects from 75 languages   │
│   Returns ISO 639-1 code      │
│   "hi", "ta", "te", "en" etc  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Node 2: retrieve_docs       │
│                               │
│   Embeds query via Azure       │
│   text-embedding-3-small       │
│                               │
│   Searches pgvector (HNSW)    │
│   Returns top 3 chunks        │
│                               │
│   Works cross-lingually —     │
│   Tamil query finds English   │
│   document chunks correctly   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│  Node 3: generate_response    │
│                               │
│   System prompt enforces:     │
│   - Answer ONLY from context  │
│   - Refuse if not in context  │
│   - Treat context as data,    │
│     never as instructions     │
│   - Respond in language: {lang}│
│   - Cite source document      │
│                               │
│   Routes by detected language: │
│   Indic → Sarvam-30B first,   │
│   English → Azure GPT-4o first │
│   Other model = fallback,      │
│   Claude Sonnet = last resort  │
└───────────────┬───────────────┘
                │
                ▼
         Final Response
      in User's Language
```

### Step 3 — Why Azure OpenAI text-embedding-3-small for Retrieval

Most RAG systems fail for Indian languages because they use English-only embedding models. When you embed a Hindi sentence with an English model, the vector has no meaningful relationship to similar Hindi content.

`text-embedding-3-small` was trained across many languages simultaneously. This means:

- A Tamil query vector sits close to relevant Tamil document vectors
- An English query about the same topic also sits close to those Tamil vectors
- Cross-language retrieval works without any translation step

This is the architectural decision that makes BharatBot's retrieval truly multilingual.

### Step 4 — Why Generation is Routed Between Sarvam-30B and Azure GPT-4o

Global models like GPT-4o were trained mostly on English. When asked to respond in Telugu, they can produce grammatically weak output or silently switch back to English. Sarvam-30B, by contrast, is trained specifically on India's scheduled languages with:

- A custom tokenizer supporting Indian scripts
- Cultural context and regional expressions
- Code-mixing support (Hinglish, Tanglish, Kanglish)

So BharatBot routes by the language `detect_language_node` assigns to the query:

- **Indic-language queries** (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi) → **Sarvam-30B** first, Azure GPT-4o as fallback
- **English queries** → **Azure GPT-4o** first, Sarvam-30B as fallback
- **Claude Sonnet** is the final fallback for either path if both primary models fail

Each model handles the languages it's actually strongest at, instead of forcing one model to cover everything.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM (Indic languages) | Sarvam-30B | Primary model for Hindi, Tamil, Telugu, and other scheduled Indian languages |
| LLM (English) | Azure GPT-4o (Azure AI Foundry) | Primary model for English queries |
| LLM Fallback | Claude Sonnet | Last-resort generation if both primary models fail |
| Embeddings | Azure OpenAI text-embedding-3-small | Cross-lingual semantic search |
| Agent Framework | LangGraph | Stateful multi-node agent |
| Vector Store | Postgres + pgvector | HNSW approximate nearest-neighbor similarity search |
| PDF Parsing | PyMuPDF | Text extraction from PDFs |
| OCR | Tesseract + lang packs | Scanned document support |
| Language Detection | lingua-py | Accurate Indic language detection |
| Backend | FastAPI | REST API server |
| Frontend | React + Vite + Tailwind CSS | Web interface, served in production via nginx |
| Memory | LangGraph MemorySaver | Session state management |
| Observability | LangSmith | Agent trace logging |
| Containerization | Docker + docker-compose | Deployment packaging |

---

## 📁 Project Structure

```
bharatbot/
├── backend/
│   ├── Dockerfile             # Python API image (Tesseract + deps)
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py        # Env-driven config: keys, model names, ports, paths
│   │   └── languages.py       # Language codes, flags, Tesseract codes
│   ├── ingestion/
│   │   ├── pdf_loader.py      # PyMuPDF + OCR fallback
│   │   ├── ocr_loader.py      # Tesseract multi-language OCR
│   │   ├── chunker.py         # Universal text splitter
│   │   ├── embedder.py        # Azure OpenAI text-embedding-3-small wrapper
│   │   ├── vector_store.py    # Postgres + pgvector connection, schema, search
│   │   └── build_vectorstore.py  # Ingestion pipeline entry point
│   ├── tools/
│   │   ├── retriever_tool.py  # pgvector search as LangChain tool
│   │   ├── translator_tool.py # Sarvam Mayura translation API
│   │   ├── language_detector.py  # lingua-py wrapper + script-range detection
│   │   └── disclaimer_tool.py # Source citation appender
│   ├── agents/
│   │   ├── state.py           # BharatBotState TypedDict
│   │   ├── nodes.py           # detect → retrieve → generate (domain-restricted)
│   │   ├── graph.py           # LangGraph compilation
│   │   └── memory.py          # Session checkpointing
│   ├── api/
│   │   ├── main.py            # FastAPI application + CORS
│   │   ├── schemas.py         # Pydantic models
│   │   └── routes/
│   │       ├── chat.py        # POST /chat
│   │       ├── upload.py      # POST /upload
│   │       └── health.py      # GET /health
│   ├── tests/
│   │   ├── test_ingestion.py
│   │   ├── test_tools.py
│   │   ├── test_agent.py
│   │   └── test_api.py
│   └── scripts/
│       ├── ingest_docs.py
│       ├── test_retrieval.py
│       └── export_langsmith.py
├── frontend/
│   ├── Dockerfile             # Multi-stage: node build → nginx serve
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── lib/
│       │   ├── api.js         # fetch wrappers for /chat, /upload
│       │   └── languages.js   # Language display metadata
│       └── components/
│           ├── Header.jsx
│           ├── Sidebar.jsx    # Upload panel + supported languages
│           ├── ChatPanel.jsx  # Message list + input bar
│           └── MessageBubble.jsx
└── Docker-compose.yaml        # Orchestrates postgres + api + frontend
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or above
- Node.js 20+ and npm (for the frontend)
- Git
- Tesseract OCR installed on your system
- Postgres with the `pgvector` extension (or just use the `postgres` service in `Docker-compose.yaml`)
- API keys for Sarvam AI, Anthropic, and Azure AI Foundry

### Install Tesseract

**Windows:**
Download installer from https://github.com/UB-Mannheim/tesseract/wiki
Add to PATH after installation.

**Mac:**
```bash
brew install tesseract
brew install tesseract-lang
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin tesseract-ocr-tam tesseract-ocr-tel
sudo apt-get install tesseract-ocr-kan tesseract-ocr-mal tesseract-ocr-ben
```

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Md-hayath/bharatbot.git
cd bharatbot
```

**2. Create a virtual environment (backend)**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install backend dependencies**

```bash
pip install -r requirements.txt
```

**4. Install frontend dependencies**

```bash
cd ../frontend
npm install
```

**5. Set up environment variables**

From the repo root:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```
SARVAM_API_KEY=your_sarvam_key
ANTHROPIC_API_KEY=your_anthropic_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=bharatbot

AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/openai/v1
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

DATABASE_URL=postgresql://bharatbot:bharatbot@localhost:5432/bharatbot
```

Get your keys:
- Sarvam API: https://dashboard.sarvam.ai
- Anthropic API: https://console.anthropic.com
- Azure AI Foundry: https://ai.azure.com — deploy a `gpt-4o` and a `text-embedding-3-small` model in your Foundry project, then copy the project's unified `/openai/v1` endpoint and key
- LangSmith: https://smith.langchain.com

`DATABASE_URL` points at the `postgres` service that ships in `Docker-compose.yaml` (pgvector-enabled Postgres). Running outside Docker? Start a local Postgres with the `pgvector` extension yourself and point this at it instead.

**6. Run the application**

Terminal 1 — Backend (from `backend/`):
```bash
uvicorn api.main:app --reload --port 8000
```

Terminal 2 — Frontend (from `frontend/`):
```bash
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Open your browser at **http://localhost:5173** (Vite's dev server port).

---

## 🐳 Run With Docker

From the repo root:
```bash
docker-compose up --build
```

Postgres, the API, and the frontend all start automatically. Open http://localhost:3000 (backend on http://localhost:8000). Ports come from `BACKEND_PORT`/`FRONTEND_PORT` in `.env`.

---

## 📖 Usage

**1. Upload a document**

Click the upload panel in the sidebar. Supports PDF, DOCX, and TXT in any language. The document is automatically chunked, embedded, and indexed.

**2. Start chatting**

Type your question in any Indian language. BharatBot automatically detects your language and responds in the same language.

**Examples:**

```
English:  "What are the main points in this document?"
Kannada:  "ಈ ದಾಖಲೆಯ ಮುಖ್ಯ ವಿಷಯ ಏನು?"
Hindi:    "इस दस्तावेज़ का मुख्य विषय क्या है?"
Telugu:   "ఈ పత్రంలో ముఖ్యమైన అంశాలు ఏమిటి?"
Tamil:    "இந்த ஆவணத்தின் முக்கிய கருத்து என்ன?"
Telugu:   "ఈ పత్రంలో ముఖ్యమైన అంశాలు ఏమిటి?"

```

**3. Cross-language queries**

You can upload a Tamil document and ask questions in Hindi. The multilingual embedding model retrieves relevant Tamil content and Sarvam-30B generates the response in Hindi.

---

## 🔌 API Reference

### POST /upload

Upload a document for indexing.

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

Response:
```json
{
  "message": "Document uploaded and indexed successfully",
  "chunks_added": 47,
  "filename": "document.pdf"
}
```

### POST /chat

Send a query and get a response.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "इस दस्तावेज़ में क्या लिखा है?",
    "session_id": "user-123"
  }'
```

Response:
```json
{
  "response": "इस दस्तावेज़ में...",
  "sources": ["document.pdf"],
  "detected_language": "hi"
}
```

### GET /health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "service": "bharatbot"
}
```

---

## 🌍 Supported Languages

| Language | Native Script | Code | Tesseract Support |
|---|---|---|---|
| Hindi | हिन्दी | hi | ✅ |
| Tamil | தமிழ் | ta | ✅ |
| Telugu | తెలుగు | te | ✅ |
| Kannada | ಕನ್ನಡ | kn | ✅ |
| Malayalam | മലയാളം | ml | ✅ |
| Bengali | বাংলা | bn | ✅ |
| Marathi | मराठी | mr | ✅ |
| Gujarati | ગુજરાતી | gu | ✅ |
| Punjabi | ਪੰਜਾਬੀ | pa | ✅ |
| Urdu | اردو | ur | ✅ |
| English | English | en | ✅ |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Run individual test modules:

```bash
pytest tests/test_ingestion.py -v
pytest tests/test_tools.py -v
pytest tests/test_agent.py -v
pytest tests/test_api.py -v
```

---

## 📊 How This Differs From Standard RAG

| Feature | Standard RAG | BharatBot |
|---|---|---|
| Language Support | English only | 22 Indian languages |
| Embedding Model | text-embedding-ada | Azure OpenAI text-embedding-3-small |
| Cross-lingual Retrieval | ❌ | ✅ |
| Script Handling | Latin only | Devanagari, Tamil, Telugu, etc. |
| OCR Support | ❌ | ✅ Tesseract multi-lang |
| LLM | GPT-4 | Sarvam-30B (Indic) + Azure GPT-4o (English), Claude fallback |
| Agent Framework | LangChain | LangGraph stateful |
| Language Detection | ❌ | lingua-py auto detect |
| Source Attribution | Basic | With chunk metadata |

---

## ⚠️ Known Limitations

- **Cross-lingual retrieval accuracy is unverified for some Indic language pairs (e.g. a Kannada document queried in English).** The retrieval embedding model was recently switched from `multilingual-e5-large` — which was purpose-trained on parallel text across 100+ languages for cross-lingual retrieval — to Azure OpenAI's `text-embedding-3-small`, a strong general-purpose multilingual embedder without published cross-lingual benchmarks for lower-resource Indic languages specifically. The retrieval pipeline (pgvector + shared embedding space) supports cross-lingual search either way; what's unproven is retrieval *quality* for these specific pairs. This is being tracked — see Roadmap.

---

## 🔮 Roadmap

- [ ] Validate cross-lingual retrieval quality under `text-embedding-3-small` for Indic language pairs (e.g. Kannada doc + English query); add translation-assisted retrieval if needed
- [ ] Voice input support using Sarvam Saaras v3 speech-to-text
- [ ] Voice output using Sarvam Bulbul v3 text-to-speech
- [ ] WhatsApp integration for rural accessibility
- [ ] Multi-document comparison queries
- [ ] Table and chart extraction from PDFs
- [ ] Fine-tuned retrieval for legal and medical documents
- [ ] Mobile responsive UI

---

## 🤝 Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change.

```bash
# Fork the repo
# Create your feature branch
git checkout -b feature/AmazingFeature

# Commit your changes
git commit -m "Add AmazingFeature"

# Push to the branch
git push origin feature/AmazingFeature

# Open a Pull Request
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgements

- [Sarvam AI](https://sarvam.ai) — for building India's sovereign LLM
- [AI4Bharat](https://ai4bharat.iitm.ac.in) — for Indic language research
- [LangChain](https://langchain.com) — for the LangGraph agent framework
- [Microsoft Azure AI Foundry](https://ai.azure.com) — for GPT-4o and text-embedding-3-small
- [pgvector](https://github.com/pgvector/pgvector) — for vector similarity search in Postgres

---

## 👤 Author

**Mohammed Hayath**

- GitHub: [@Md-hayath](https://github.com/Md-hayath)
- LinkedIn: [Mohammed Hayath](https://linkedin.com/in/mohammed-hayath-b675a0259/)
- Portfolio: [hayath78.biz](https://www.datascienceportfol.io/hayath4863)

---

<div align="center">

⭐ Star this repo if you found it useful

*Built with ❤️ for Bharat*

</div>
```