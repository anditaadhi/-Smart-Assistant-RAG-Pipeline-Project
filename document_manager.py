import os
import json
import logging
from datetime import datetime
from kafka import KafkaProducer

# Format-specific parsers
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import csv

logger = logging.getLogger(__name__)

def get_kafka_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception:
        return None
    
def resolve_allowed_roles(file_name, uploader_role):
    name = file_name.lower()
    if name.startswith("hr_"):
        return ["admin", "HR"]
    elif name.startswith("eng_"):
        return ["admin", "engineer"]
    elif name.startswith("policy_"):
        return ["admin", "engineer", "HR"]
    else:
        return ["admin", uploader_role]    

def parse_file(file_path, file_name):
    """
    
    [(page_number, content, section_heading)] list
    """
    ext = file_name.rsplit('.', 1)[-1].lower()
    pages = []

    if ext == "pdf":
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                lines = text.strip().splitlines()
                heading = lines[0][:80] if lines else "N/A"
                pages.append((i + 1, text, heading))

    elif ext == "docx":
        doc = Document(file_path)
        current_heading = "N/A"
        current_text = ""
        page_num = 1
        for para in doc.paragraphs:
            if para.style.name.startswith("Heading"):
                if current_text.strip():
                    pages.append((page_num, current_text, current_heading))
                    page_num += 1
                current_heading = para.text[:80]
                current_text = ""
            else:
                current_text += para.text + "\n"
        if current_text.strip():
            pages.append((page_num, current_text, current_heading))

    elif ext == "html":
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        heading_tag = soup.find(["h1", "h2", "h3"])
        heading = heading_tag.text[:80] if heading_tag else "N/A"
        text = soup.get_text(separator="\n")
        if text.strip():
            pages.append((1, text, heading))

    elif ext == "csv":
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        header = ", ".join(rows[0]) if rows else "N/A"
        chunk_size = 50
        for i, chunk_start in enumerate(range(1, len(rows), chunk_size)):
            chunk_rows = rows[chunk_start:chunk_start + chunk_size]
            text = "\n".join([", ".join(row) for row in chunk_rows])
            if text.strip():
                pages.append((i + 1, text, header))

    else:
        logger.warning(f"Unsupported file format: {ext}")

    return pages

def save_and_index(uploaded_file, producer, topic, uploader_role):
    save_folder = "uploaded_docs"
    os.makedirs(save_folder, exist_ok=True)
    file_path = os.path.join(save_folder, uploaded_file.name)

    if os.path.exists(file_path):
        return False, f"⚠️ '{uploaded_file.name}' already has exist."

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if not producer:
        return False, "❌ Not connected to Kafka."

    try:
        pages = parse_file(file_path, uploaded_file.name)
        if not pages:
            return False, "❌ No info created from file."

        timestamp = datetime.utcnow().isoformat()
        allowed_roles = resolve_allowed_roles(uploaded_file.name, uploader_role)
        for page_num, content, heading in pages:
            message = {
                "action": "upload",
                "file_name": uploaded_file.name,
                "page_number": page_num,
                "section": heading,
                "content": content,
                "timestamp": timestamp,
                "version": "1.0",
                "allowed_roles": allowed_roles
            }
            producer.send(topic, value=message)

        producer.flush()
        logger.info(f"📁 UPLOAD | File: {uploaded_file.name} | Pages: {len(pages)}")
        return True, f"✅ '{uploaded_file.name}' successfully sent. ({len(pages)} processed page.)"

    except Exception as e:
        logger.error(f"Parse/Kafka Error: {e}")
        return False, f"❌ Process Error: {str(e)}"

def delete_document(file_name, producer, topic):
    save_folder = "uploaded_docs"
    file_path = os.path.join(save_folder, file_name)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)

        if producer:
            producer.send(topic, value={
                "action": "delete",
                "file_name": file_name,
                "timestamp": datetime.utcnow().isoformat()
            })
            producer.flush()

        logger.info(f"🗑️ DELETE | File: {file_name}")
        return True, f"🗑️ '{file_name}' deleted successfully."

    except Exception as e:
        return False, f"❌ Delete Error: {str(e)}"