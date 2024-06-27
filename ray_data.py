from pathlib import Path
import ray
from doc_process import download_all

def ray_dataset(folder):
    # Ray dataset
    document_dir = Path(folder)
    ds = ray.data.from_items([{"path": path.absolute()} for path in document_dir.rglob("*.html") if not path.is_dir()])
    print(f"{ds.count()} documents")

if __name__ == "__main__":
    working_dir = "downloaded_docs"
    start_url = "https://python.langchain.com/docs/expression_language/"
    folder = working_dir
    download_all(start_url, folder, max_workers=10)
    ray_dataset(folder)

