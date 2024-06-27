from functools import partial
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import numpy as np
from ray.data import ActorPoolStrategy
from preprocess.ray_data import ray_dataset

class EmbedChunks:
    def __init__(self):
        self.embedding_model = get_embedding_model()

    def __call__(self, batch):
        embeddings = self.embedding_model.embed_documents(batch["text"])
        return {"text": batch["text"], "path": batch["path"], "embeddings": embeddings}

def get_embedding_model():
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return embedding_model

# Defining our text splitting function
def chunking(document, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len)

    chunks = text_splitter.create_documents(
        texts=[document["text"]], 
        metadatas=[{"path": document["path"]}])
    
    return [{"text": chunk.page_content, "path": chunk.metadata["path"]} for chunk in chunks]

def indexer(content_ds):

    chunks_ds = content_ds.flat_map(partial(
        chunking, 
        chunk_size=512, 
        chunk_overlap=50))
    
    print(f"{chunks_ds.count()} chunks")
    
    # embedded_chunks = chunks_ds.map_batches(
    #     EmbedChunks,
    #     batch_size=100, 
    #     num_gpus=1,
    #     concurrency=1)
    
    
    
