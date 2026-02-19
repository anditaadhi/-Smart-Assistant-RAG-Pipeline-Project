# 🤖 Smart Assistant — RAG Pipeline

An enterprise-grade knowledge assistant. Documents are processed via Kafka, indexed into Qdrant, and queries are answered with cited sources.

```
Files → Kafka → Qdrant (VectorDB) → Ollama (LLM) → Streamlit (UI)
```

> Supports **PDF, DOCX, HTML, CSV** formats.

---

## 🏗️ Architecture

| Component | Role |
|-----------|------|
| **Kafka** | Event-driven orchestration (upload / delete / update) |
| **Qdrant** | Stores chunks & embeddings, handles semantic retrieval |
| **Ollama (llama3.2)** | Local LLM, generates responses with citations |
| **Streamlit** | Web UI with Role-Based Access Control (RBAC) |

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Docker & Docker Compose

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat&logo=apachekafka&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?style=flat&logo=qdrant&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-llama3.2-black?style=flat&logo=ollama&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

### Steps

**1. Clone the repository**
```bash
git clone <repo-url>
cd rag-project
```

**2. Create the `.env` file**
```bash
cp .env.example .env
```
```env
ADMIN_PASSWORD=your_admin_password
USER_PASSWORD=your_user_password
```

**3. Start Docker services**
```bash
docker-compose up -d
```

**4. Pull the Ollama model**
```bash
docker exec ollama_llm ollama pull llama3.2
```

**5. Install dependencies**
```bash
pip install -r requirements.txt
```

**6. Start the consumer** *(Terminal 1)*
```bash
python consumer.py
```

**7. Launch the application** *(Terminal 2)*
```bash
streamlit run app.py
```

---

## 🚀 Usage

### Login

| Username | Role |
|----------|------|
| `admin` | admin |
| `user` | engineer |
| `user2` | hr |

### Document Uploading

RBAC is automatically applied based on the filename prefix:

| Prefix | Access |
|--------|--------|
| `hr_` | admin, HR |
| `eng_` | admin, engineer |
| `policy_` | admin, engineer, HR |
| *(no prefix)* | admin + uploader's role |

> **Example:** `hr_recruitment.pdf` → accessible only by admin and HR.

### Querying
Ask questions via the chat interface. Citations like `[1]` `[2]` in responses link to the **Reference Sources** panel, showing document name, page, and similarity score.

### Audit Log
Admin users can enable **View Audit Logs** in the sidebar to monitor all queries and document operations.

---

## 🔒 Security

- **Credentials** — stored in `.env`, never hardcoded
- **RBAC** — every chunk tagged with `allowed_roles`; queries filtered by role
- **Masking** — phone numbers and emails in responses are auto-masked
- **Audit Log** — tracks who asked what and which documents were used

---

## 🔧 Technical Notes

| Parameter | Value |
|-----------|-------|
| Chunk size | 800 tokens |
| Overlap | 150 tokens |
| Embedding model | `all-MiniLM-L6-v2` (384 dims) |
| Qdrant collection | `alstom_docs` — cosine similarity |
| Retrieval | Top-3 semantic search |

---

## ⚠️ Known Limitations

- **Performance** — Ollama runs on CPU; consider GPU or OpenAI/Anthropic APIs for production.
- **Scalability** — Single consumer handles the full pipeline. A production setup should use separate Kafka consumer groups for OCR, chunking, and embedding.
- **User management** — Currently `.env`-based; LDAP/SSO recommended for production.
- **Storage & logging** — For production, use S3 for metadata and ELK Stack for centralized logging.
