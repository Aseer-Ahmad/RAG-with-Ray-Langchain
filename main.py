from preprocess.ray_data import ray_dataset
from rag.indexing import indexer
from env import setup_env

def main():
    working_dir = "downloaded_docs"
    start_url = "https://python.langchain.com/docs/expression_language/"

    setup_env()
    content_ds = ray_dataset(start_url, working_dir)

    indexer(content_ds)

if __name__ == "__main__":
    main()