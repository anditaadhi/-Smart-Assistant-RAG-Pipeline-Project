import streamlit as st
import logging
import os
from auth import initialize_auth, login_screen
from model_utils import load_ai_models, get_ai_response
from document_manager import get_kafka_producer, save_and_index, delete_document
import re

st.set_page_config(page_title="Alstom Knowledge Assistant", page_icon="🚂", layout="wide")

def apply_masking(text):
    """Hassas içerikleri (Telefon, E-posta) maskeler."""
    # Telefon numaralarını maskele (Örn: 05xx xxx xx xx)
    text = re.sub(r'\d{10,11}', '[MASKED_PHONE]', text)
    # E-postaları maskele
    text = re.sub(r'\S+@\S+', '[MASKED_EMAIL]', text)
    return text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alstom_audit.log"),
        logging.StreamHandler()                
    ]
)
logger = logging.getLogger(__name__)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("qdrant_client").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("ollama").setLevel(logging.WARNING)

# Config
QDRANT_HOST, QDRANT_PORT = "localhost", 6333
COLLECTION_NAME = "alstom_docs"
KAFKA_TOPIC = 'document_processing'
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# 
users = initialize_auth()
login_screen(users)

if not st.session_state.get("logged_in"):
    st.stop()

producer = get_kafka_producer()
embedder, qdrant = load_ai_models(QDRANT_HOST, QDRANT_PORT, EMBEDDING_MODEL_NAME)

if "messages" not in st.session_state: 
    st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.title("🚂 Session Info")
    st.info(f"👤 **User:** {st.session_state.username}\n\n🛡️ **Role:** {st.session_state.role}")
    
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()
    st.header("📝 Chat History")
    if st.session_state.messages:
        history_count = 0
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                st.caption(f"💬 {msg['content'][:35]}...")
                history_count += 1
            if history_count >= 5: break
    else:
        st.caption("No history yet.")

    if st.session_state.role == "admin":
        st.divider()
        if st.sidebar.checkbox("🔍 View Audit Logs (Admin)"):
            st.subheader("🛡️ System Audit Trail")
            try:
                with open("alstom_audit.log", "r", encoding="utf-8") as f:
                    log_data = f.readlines()
                    
                    audit_logs = []
                    for line in log_data:
                        if any(tag in line for tag in ["🛡️ AUDIT", "📁 UPLOAD", "🗑️ DELETE"]):
                            clean_line = line.split(" - INFO - ")[-1] if " - INFO - " in line else line
                            timestamp = line[:19]
                            audit_logs.append(f"⏱️ {timestamp} | {clean_line.strip()}")
                    
                    if audit_logs:
                        for log in reversed(audit_logs[-20:]): 
                            st.caption(log)
                    else:
                        st.caption("Not found audit log yet.")
            except FileNotFoundError:
                st.caption("No created log file yet.")

# --- ANA PANEL ---
st.title("🤖 Alstom Knowledge Assistant")
st.divider()

col1, col2 = st.columns([1.5, 2.5], gap="large")

with col1:
    st.subheader("📁 Document Management")
    uploaded_file = st.file_uploader("Upload PDF, CSV, DOCX or HTML", type=["pdf", "csv", "html", "docx"])
    
    if uploaded_file:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Send", use_container_width=True, type="primary"):
                success, message = save_and_index(uploaded_file, producer, KAFKA_TOPIC, st.session_state.role)
                if success: st.success(message)
                else: st.error(message)
        
        with c2:
            # Silme Butonu
            if st.button("🗑️ Delete", use_container_width=True):
                success, message = delete_document(uploaded_file.name, producer, KAFKA_TOPIC)
                if success:
                    st.warning(message)
                    logger.info(f"🗑️ DELETE | User: {st.session_state.username} | File: {uploaded_file.name}")
                    st.rerun()
                else:
                    st.error(message)

with col2:
    st.subheader("💬 Chat")
    chat_container = st.container(height=450)
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "citations" in msg and msg["citations"]:
                    with st.expander("🔍 Reference Sources"):
                        for cit in msg["citations"]: st.caption(cit)

    
    if prompt := st.chat_input("Ask about something..."):
        if prompt.strip():
            masked_prompt = apply_masking(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"): st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing documentation..."):
                        try:
                            d_name = uploaded_file.name if uploaded_file else None
                            answer, citations = get_ai_response(
                                masked_prompt, 
                                st.session_state.role, 
                                embedder, 
                                qdrant, 
                                COLLECTION_NAME, 
                                OLLAMA_URL, 
                                OLLAMA_MODEL, 
                                doc_name=d_name
                            )
                            
                            logger.info(f"🛡️ AUDIT | User: {st.session_state.username} | Query: {prompt}")
                            
                            st.markdown(answer)
                            if citations:
                                with st.expander("🔍 Reference Sources"):
                                    for cit in citations: st.caption(cit)
                                    
                            
                            st.session_state.messages.append({"role": "assistant", "content": answer, "citations": citations})
                            st.rerun()
                        except Exception as e:
                            st.error(f"System Error: {e}")
                            
                            