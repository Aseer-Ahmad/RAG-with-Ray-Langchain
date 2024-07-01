from functools import partial
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import numpy as np
from ray.data import ActorPoolStrategy
from preprocess.ray_data import ray_dataset
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct
import ray

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

def chunkEmbed(content_ds):

    chunks_ds = content_ds.flat_map(partial(
        chunking, 
        chunk_size=512, 
        chunk_overlap=50))
    
    print(f"chunking completed with  : {chunks_ds.count()} chunks")
    
    embedded_chunks = chunks_ds.map_batches(
        EmbedChunks,
        batch_size=50, 
        num_gpus=1,
        concurrency=1)
    
    print(f"embedding completed with  : {chunks_ds.count()} chunks")

    return embedded_chunks

def store_results(df, client, collection_name="documents"):

    print("creating points to begin indexing in Qdrant vector store.")

	  # Defining our data structure
    points = [
        # PointStruct is the data classs used in Qdrant
        PointStruct(
            id=hash(path),  # Unique ID for each point
            vector=embedding,
            payload={
                "text": text,
                "source": path
            }
        )
        for text, path, embedding in df.iter_rows() #zip(df["text"], df["path"], df["embeddings"])
    ]
		
		# Adding our data points to the collection
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    print("all points added to Qdrant")

@ray.remote
def indexer(content_ds):

    embedded_chunks = chunkEmbed(content_ds)
    embedded_chunks = embedded_chunks.to_pandas()
    embedding_size = 256

    # print(embedded_chunks.iter_rows())
    # count = 0
    # for row in embedded_chunks.iter_rows():
    #     print(row)
    #     if count==3:
    #         break

    # Initalizing a local client in-memory
    # client = QdrantClient(":memory:")

    # client.recreate_collection(
    #     collection_name="documents",
    #     vectors_config=VectorParams(size=embedding_size, distance=Distance.COSINE),
    # )

    # print(embedded_chunks)

    # store_results(embedded_chunks, client)