import json
import logging
import time
import uuid
from datetime import datetime
from kafka import KafkaConsumer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_logs.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logging.getLogger("qdrant_client").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)
logging.getLogger("kafka.conn").setLevel(logging.WARNING)

# System Info
KAFKA_TOPIC = 'document_processing'
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "alstom_docs"

model = SentenceTransformer('all-MiniLM-L6-v2')

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    length_function=len
)

# Qdrant Setup
client = QdrantClient(url=QDRANT_URL)
try:
    client.get_collection(COLLECTION_NAME)
except:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def process_event(data):
    action = data.get('action', 'upload') #
    file_name = data.get('file_name', 'Unknown_Doc.pdf')
    
    # Delete Action
    if action == 'delete':
        try:
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(
                    must=[FieldCondition(key="doc_name", match=MatchValue(value=file_name))]
                )
            )
            logger.info(f"🗑️  DELETED  | {file_name}")
        except Exception as e:
            logger.error(f"DELETE ERROR: {e}")
        return

    # Upload/Update Action
    content = data.get('content', '')
    page_num = data.get('page_number', 0)
    
    if not content.strip():
        return

    chunks = text_splitter.split_text(content)
    points_to_upsert = []
    
    for chunk in chunks:
        chunk_id = uuid.uuid4().hex
        vector = model.encode(chunk).tolist()
        
        payload = {
            "doc_name": file_name,
            "page_number": page_num,
            "section": data.get("section", "N/A"),
            "timestamp": data.get("timestamp", ""),
            "version": data.get("version", "1.0"),
            "text": chunk,
            "allowed_roles": data.get("allowed_roles", ["admin"])
        }
        points_to_upsert.append(PointStruct(id=chunk_id, vector=vector, payload=payload))

    if points_to_upsert:
        client.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert)
        logger.info(f"✅ INDEXED  | {file_name} | Page {page_num} | Chunks: {len(points_to_upsert)}")

def connect_kafka():
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id='alstom_processor_group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                api_version=(0, 10, 1),
                auto_offset_reset='earliest'
            )
            return consumer
        except Exception as e:
            time.sleep(5)

# Main
consumer = connect_kafka()

try:
    for message in consumer:
        process_event(message.value) #
except Exception as e:
    logger.critical(f"SYSTEM STOPPED: {e}")