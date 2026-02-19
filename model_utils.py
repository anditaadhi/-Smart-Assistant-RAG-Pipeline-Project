import requests
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue

def load_ai_models(host, port, model_name):
    embedder = SentenceTransformer(model_name)
    qdrant = QdrantClient(host=host, port=port)
    return embedder, qdrant

def get_ai_response(prompt, role, embedder, qdrant, collection, ollama_url, model, doc_name=None):
    # just uploadded file once
    must_conditions = [FieldCondition(key="allowed_roles", match=MatchValue(value=role))]
    if doc_name:
        must_conditions.append(FieldCondition(key="doc_name", match=MatchValue(value=doc_name)))
    
    role_filter = Filter(must=must_conditions)
    query_vector = embedder.encode(prompt).tolist()
    
    #why we use query points bcs need to details about doc like page score
    results = qdrant.query_points(
        collection_name=collection, 
        query=query_vector, 
        query_filter=role_filter, 
        limit=3
    ).points
    
    context = ""
    citations = []
    for i, r in enumerate(results):
        text = r.payload.get('text', '')
        context += f"[{i+1}] {text}\n\n"
        doc = r.payload.get('doc_name', 'Unknown')
        page = r.payload.get('page_number', 'N/A')
        score = r.score 
        citations.append(f"📄 {doc} | 📑 Page: {page} | 🎯 Score: {score:.2f}")
    
    sys_prompt = f"""You are a document assistant. Answer ONLY based on the context below. 
Do not use any external knowledge. If the answer is not in the context, say "I could not find this in the provided documents."
Cite sources using [1], [2] etc.

Context:
{context}

Question: {prompt}"""
    resp = requests.post(ollama_url, json={"model": model, "messages": [{"role": "user", "content": sys_prompt}], "stream": False})
    

    return resp.json().get("message", {}).get("content", "Error"), citations
