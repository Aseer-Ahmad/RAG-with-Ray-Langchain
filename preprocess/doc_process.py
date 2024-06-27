import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import os
from env import setup_env

def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)  # Remove problematic characters
    filename = re.sub(r'[^\x00-\x7F]+', '_', filename)  # Replace non-ASCII characters
    return filename

def is_valid(url):
    parsed = urlparse(url)
    valid = bool(parsed.netloc) and parsed.path.startswith("/v0.1/docs/expression_language/") 
    return valid

def save_html(url, folder):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else os.path.basename(urlparse(url).path)
        sanitized_title = sanitize_filename(title)
        filename = os.path.join(folder, sanitized_title.replace(" ", "_") + ".html")

        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            print(f"saving {url} to {filename}")

            links = [urljoin(url, link.get('href')) for link in soup.find_all('a') if link.get('href') and is_valid(urljoin(url, link.get('href')))]
            return links
        else:
            print(f"file from start url : {url} already exist in {folder}")
            return []
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return []

def download_all(start_url, folder, max_workers=5):
    visited = set()
    to_visit = {start_url}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while to_visit:
            future_to_url = {executor.submit(save_html, url, folder): url for url in to_visit}
            visited.update(to_visit)
            to_visit.clear()

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    new_links = future.result()
                    for link in new_links:
                        if link not in visited:
                            to_visit.add(link)
                except Exception as e:
                    print(f"Error with future for {url}: {e}")

if __name__ == "__main__":
    working_dir = "downloaded_docs"

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    start_url = "https://python.langchain.com/docs/expression_language/"
    setup_env()
    download_all(start_url, working_dir, max_workers=10)
