from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
import uuid
import os
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from pydantic import BaseModel
from openai import OpenAI
import tempfile

load_dotenv()
app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

@app.post('/api/query')
async def api_query(req: QueryRequest):
    query_vec = embed_texts([req.question])[0]
    store = QdrantStorage()
    found = store.search(query_vec, req.top_k)
    context_block = "\n\n".join(f"- {c}" for c in found["contexts"])
    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {req.question}\n"
        "Answer concisely using the context above."
    )
    
    client = OpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url='https://api.groq.com/openai/v1')
    res = client.chat.completions.create(
        model='groq/compound',
        max_tokens=1024,
        temperature=0.2,
        messages=[
            {'role': 'system', 'content': 'You answer questions using only the provided context.'},
            {'role': 'user', 'content': user_content}
        ]
    )
    answer = res.choices[0].message.content.strip()
    return {'answer': answer, 'sources': found['sources'], 'num_contexts': len(found['contexts'])}

@app.post('/api/upload')
async def api_upload(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    chunks = load_and_chunk_pdf(tmp_path)
    vecs = embed_texts(chunks)
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file.filename}:{i}")) for i in range(len(chunks))]
    payloads = [{"source": file.filename, "text": chunks[i]} for i in range(len(chunks))]
    
    QdrantStorage().clear()
    QdrantStorage().upsert(ids, vecs, payloads)
    os.remove(tmp_path)
    return {"status": "success", "ingested": len(chunks)}