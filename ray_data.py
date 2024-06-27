from pathlib import Path
import ray
from doc_process import download_all
from bs4 import BeautifulSoup, NavigableString

def extract_text_from_element(element):
    texts = []
    for elem in element.descendants:
        if isinstance(elem, NavigableString):
            text = elem.strip()
            if text:
                texts.append(text)
    return "\n".join(texts)

def extract_main_content(record):
    with open(record["path"], "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    main_content = soup.find(['main', 'article'])  # Add any other tags or class_="some-class-name" here
    if main_content:
        text = extract_text_from_element(main_content)
    else:
        text = "No main content found."

    path = record["path"]
    return {"path": path, "text": text}

def ray_dataset(folder):
    # Ray dataset
    document_dir = Path(folder)
    print("creating ray data from documents")
    ds = ray.data.from_items([{"path": path.absolute()} for path in document_dir.rglob("*.html") if not path.is_dir()])
    print(f"{ds.count()} documents processed")
    print(f"cleaning html files for text and adding to ray dataset")
    content_ds = ds.map(extract_main_content)
    content_ds.count()

if __name__ == "__main__":
    working_dir = "downloaded_docs"
    start_url = "https://python.langchain.com/docs/expression_language/"
    folder = working_dir
    download_all(start_url, folder, max_workers=10)
    ray_dataset(folder)

