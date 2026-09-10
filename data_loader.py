import os
import requests
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter

EMBED_DIM = 384
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, 'text', None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    hf_token = os.getenv('HF_TOKEN')
    if not hf_token:
        raise ValueError('HF_TOKEN environment variable is not set!')
        
    api_url = 'https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction'
    headers = {'Authorization': f'Bearer {hf_token}'}
    
    response = requests.post(api_url, headers=headers, json={'inputs': texts, 'options': {'wait_for_model': True}})
    response.raise_for_status()
    return response.json()
