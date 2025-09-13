import os

import arxiv
import requests


# Download arxiv papers
def download_arxiv_papers():
    datadir = os.getenv("INLINE_DATA_VOLUME", "/opt/data")
    os.makedirs(datadir, exist_ok=True)
    client = arxiv.Client()
    search = arxiv.Search(
        query="RAG", max_results=20, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = client.results(search)
    for result in results:
        filename = os.path.join(datadir, f"{result.title}.pdf")
        if os.path.exists(filename):
            print(f"Skipping {result.title} as it already exists")
            continue
        try:
            response = requests.get(result.pdf_url)
            response.raise_for_status()
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded {result.title}")
        except Exception as e:
            print(f"Failed to download {result.title}: {e}")
