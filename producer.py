import os
import json
from kafka import KafkaProducer
from PyPDF2 import PdfReader


producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(0, 10, 1)
)

TOPIC_NAME = 'document_processing'

def process_and_send_pdf(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} Not found!")
        return

    print(f"📄 File is reading...: {file_path}")
    reader = PdfReader(file_path)
    file_name = os.path.basename(file_path)
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            message = {
                "file_name": file_name,
                "page_number": page_num + 1,
                "content": text
            }
            producer.send(TOPIC_NAME, value=message)
            print(f"✅ Page {page_num + 1} Sent to Kafka.")

    producer.flush()
    print("🚀 Document has sent successfully Kafka Query!")

if __name__ == "__main__":
    pdf_files = [f for f in os.listdir('data') if f.endswith('.pdf')]
    
    if pdf_files:
        target_pdf = os.path.join('data', pdf_files[0])
        process_and_send_pdf(target_pdf)
    else:
        print("❌ Not found processing 'data' file!")