# BharatBot-Indian-Language-RagAgent-

# 🇮🇳 BharatBot — Multilingual Indian Language RAG Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=for-the-badge&logo=streamlit)
![Sarvam AI](https://img.shields.io/badge/Sarvam--30B-LLM-orange?style=for-the-badge)
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
- 🔍 **Semantic Search** — Uses multilingual vector embeddings to find the most relevant content even when query language differs from document language
- ⚡ **Real-time Streaming** — Fast responses powered by Sarvam-30B with Claude Sonnet fallback
- 📊 **Source Attribution** — Every answer cites the exact source document it retrieved from
- 🛡️ **Scanned Document Support** — OCR fallback using Tesseract for image-based PDFs
- 🔁 **Automatic Fallback** — If Sarvam API is unavailable, seamlessly switches to Claude Sonnet

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                    Streamlit Web App                         │
│         Upload Panel │ Chat Window │ Language Badge          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP REST
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
│  FAISS Index        │      │  Node 3: generate_response      │
└─────────────────────┘      └──────────────┬─────────────────┘
                                            │
                             ┌──────────────▼─────────────────┐
                             │          LLM LAYER             │
                             │                                 │
                             │  Primary:  Sarvam-30B           │
                             │  Fallback: Claude Sonnet        │
                             │                                 │
                             │  Embeddings:                    │
                             │  multilingual-e5-large          │
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
│    multilingual-e5-large Embeddings     │
│                                         │
│  Each chunk gets prefix "passage: "     │
│  and is converted to a 1024-dim vector  │
│                                         │
│  This model understands semantic        │
│  meaning across 100+ languages in the  │
│  SAME vector space — critical for       │
│  cross-language retrieval              │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│           FAISS Vector Store            │
│                                         │
│  IndexFlatL2 — exact L2 distance search │
│  Metadata stored separately in pickle   │
│  Contains: text, source file, chunk_id  │
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
│   Embeds query with prefix    │
│   "query: " + user_text       │
│                               │
│   Searches FAISS index        │
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
│   System prompt instructs:    │
│   "Respond in language: {lang}│
│                               │
│   Sends context + query       │
│   to Sarvam-30B               │
│                               │
│   On failure → Claude Sonnet  │
│                               │
│   Cites source document       │
└───────────────┬───────────────┘
                │
                ▼
         Final Response
      in User's Language
```

### Step 3 — Why multilingual-e5-large is the Key

Most RAG systems fail for Indian languages because they use English-only embedding models. When you embed a Hindi sentence with an English model, the vector has no meaningful relationship to similar Hindi content.

`intfloat/multilingual-e5-large` was trained on 100+ languages simultaneously. This means:

- A Tamil query vector sits close to relevant Tamil document vectors
- An English query about the same topic also sits close to those Tamil vectors
- Cross-language retrieval works without any translation step

This is the architectural decision that makes BharatBot truly multilingual.

### Step 4 — Why Sarvam-30B as the LLM

Sarvam-30B was released in February 2026 trained specifically on India's 22 scheduled languages with:

- A custom tokenizer supporting all 12 Indian scripts
- Cultural context and regional expressions
- Code-mixing support (Hinglish, Tanglish, Kanglish)
- 32,000 token context window for real-time conversations

Global models like GPT-4 were trained mostly on English. When asked to respond in Telugu, they often produce grammatically weak output or silently switch back to English. Sarvam-30B was built from the ground up for this exact use case.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM Primary | Sarvam-30B | Indic language generation |
| LLM Fallback | Claude Sonnet | English and fallback generation |
| Embeddings | multilingual-e5-large | Cross-lingual semantic search |
| Agent Framework | LangGraph | Stateful multi-node agent |
| Vector Store | FAISS | Fast similarity search |
| PDF Parsing | PyMuPDF | Text extraction from PDFs |
| OCR | Tesseract + lang packs | Scanned document support |
| Language Detection | lingua-py | Accurate Indic language detection |
| Backend | FastAPI | REST API server |
| Frontend | Streamlit | Web interface |
| Memory | LangGraph MemorySaver | Session state management |
| Observability | LangSmith | Agent trace logging |
| Containerization | Docker + docker-compose | Deployment packaging |

---

## 📁 Project Structure

```
bharatbot/
├── config/
│   ├── settings.py           # API keys, model names, paths
│   └── languages.py          # Language codes, flags, Tesseract codes
├── data/
│   ├── raw/                  # Uploaded documents by language
│   ├── processed/            # Cleaned text files
│   └── vector_store/         # FAISS index + metadata
├── ingestion/
│   ├── pdf_loader.py         # PyMuPDF + OCR fallback
│   ├── ocr_loader.py         # Tesseract multi-language OCR
│   ├── chunker.py            # Universal text splitter
│   ├── embedder.py           # multilingual-e5-large wrapper
│   └── build_vectorstore.py  # Ingestion pipeline entry point
├── tools/
│   ├── retriever_tool.py     # FAISS search as LangChain tool
│   ├── translator_tool.py    # Sarvam Mayura translation API
│   ├── language_detector.py  # lingua-py wrapper
│   └── disclaimer_tool.py    # Source citation appender
├── agents/
│   ├── state.py              # BharatBotState TypedDict
│   ├── nodes.py              # detect → retrieve → generate
│   ├── graph.py              # LangGraph compilation
│   └── memory.py             # Session checkpointing
├── api/
│   ├── main.py               # FastAPI application
│   ├── schemas.py            # Pydantic models
│   └── routes/
│       ├── chat.py           # POST /chat
│       ├── upload.py         # POST /upload
│       └── health.py         # GET /health
├── ui/
│   ├── app.py                # Streamlit frontend
│   └── components/
│       ├── language_selector.py
│       ├── chat_window.py
│       └── upload_panel.py
├── tests/
│   ├── test_ingestion.py
│   ├── test_tools.py
│   ├── test_agent.py
│   └── test_api.py
└── scripts/
    ├── ingest_docs.py
    ├── test_retrieval.py
    └── export_langsmith.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or above
- Git
- Tesseract OCR installed on your system
- API keys for Sarvam AI and Anthropic

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

**2. Create virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

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
```

Get your keys:
- Sarvam API: https://dashboard.sarvam.ai
- Anthropic API: https://console.anthropic.com
- LangSmith: https://smith.langchain.com

**5. Run the application**

Terminal 1 — Backend:
```bash
uvicorn api.main:app --reload --port 8000
```

Terminal 2 — Frontend:
```bash
streamlit run ui/app.py
```

Open your browser at **http://localhost:8501**

---

## 🐳 Run With Docker

```bash
docker-compose up --build
```

Both API and UI start automatically. Open http://localhost:8501

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
| Embedding Model | text-embedding-ada | multilingual-e5-large |
| Cross-lingual Retrieval | ❌ | ✅ |
| Script Handling | Latin only | Devanagari, Tamil, Telugu, etc. |
| OCR Support | ❌ | ✅ Tesseract multi-lang |
| LLM | GPT-4 | Sarvam-30B + Claude fallback |
| Agent Framework | LangChain | LangGraph stateful |
| Language Detection | ❌ | lingua-py auto detect |
| Source Attribution | Basic | With chunk metadata |

---

## 🔮 Roadmap

- [ ] Voice input support using Sarvam Saaras v3 speech-to-text
- [ ] Voice output using Sarvam Bulbul v3 text-to-speech
- [ ] WhatsApp integration for rural accessibility
- [ ] Multi-document comparison queries
- [ ] Pinecone vector store for production scale
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
- [Hugging Face](https://huggingface.co) — for multilingual-e5-large embeddings
- [FAISS](https://github.com/facebookresearch/faiss) — for vector similarity search

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