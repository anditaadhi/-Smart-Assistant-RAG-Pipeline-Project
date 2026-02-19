# -Smart-Assistant-RAG-Pipeline-Project

An enterprise-grade RAG (Retrieval-Augmented Generation) based knowledge assistant. It processes documents in PDF, DOCX, HTML, and CSV formats via Kafka, indexes them into the Qdrant vector database, and answers user queries with cited sources.

## Architecture

Files → Kafka → VectorDB (Qdrant) → RAG (Ollama) → UI (Streamlit)

- **Files**: Supports PDF, DOCX, HTML, and CSV formats.
- **Kafka**: Event-driven orchestration layer (handles upload/delete/update events).
- **Qdrant**: Stores chunks and embeddings; handles semantic retrieval.
- **Ollama (llama3.2)**: Local LLM that generates responses with citations.
- **Streamlit**: Web interface featuring Role-Based Access Control (RBAC).

## Installation

### Prerequisites

- Python 3.10+
- Docker & Docker Compose

### 1. Clone the Repository

bash
git clone <repo-url>
cd rag-project

2. Create the .env File

cp .env.example .env

Fill in the .env file:

ADMIN_PASSWORD=your_admin_password
USER_PASSWORD=your_user_password

3. Start Docker Services
   docker-compose up -d

4. Pull the Ollama Model
   docker exec ollama_llm ollama pull llama3.2

5. Install Dependencies
    pip install -r requirements.txt

6. Start the Consumer (Terminal 1)
   python consumer.py

7. Launch the Application (Terminal 2)
   streamlit run app.py

Usage
Login
User	Role
admin	admin
user  engineer
user2 hr
...

Document Uploading

RBAC is automatically applied based on the filename prefix:
Prefix	Access Level
hr_	admin, HR
eng_	admin, engineer
policy_	admin, engineer, HR
No prefix	admin + the uploader's role

Example: hr_recruitment.pdf → Accessible only by admin and HR.

Querying

Once documents are uploaded, you can ask questions via the chat interface. Citations like [1] and [2] within the response are displayed in the "Reference Sources" panel, showing the document name, page number, and similarity score.

Audit Log
Admin users can monitor all queries and document operations by checking the "View Audit Logs" box in the sidebar.

Security

    Credentials: User credentials are stored in the .env file, not hardcoded.

    RBAC: Every chunk is tagged with allowed_roles metadata; queries are filtered by role.

    Masking: Phone numbers and email addresses in responses are automatically masked.

    Audit Log: Tracks who asked what and which documents were used to generate the response.

Technical Notes

    Chunk size: 800 tokens, Overlap: 150 tokens.

    Embedding model: all-MiniLM-L6-v2 (384 dimensions).

    Qdrant collection: alstom_docs, using cosine similarity.

    Retrieval: Top-3 semantic search.

Known Limitations

    Response times may be slow as Ollama runs on a local CPU. For production, switching to GPU or OpenAI/Anthropic APIs is recommended.

    The current single consumer handles the entire pipeline (parsing, chunking, embedding) sequentially. In a scalable version, separate Kafka consumer groups should be defined for OCR, chunking, and embedding.

    RBAC user management is currently .env based. LDAP/SSO integration is recommended for production environments.

    For production environments, using tools such as S3 for metadata storage and the ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging is highly recommended.


