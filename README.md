# SAMRISE — Simple Search Engine Indexer

A polished educational web app that demonstrates how a simple search engine indexer works. It accepts manually added documents, processes their text, builds an inverted index, and retrieves ranked results. **It does not crawl the web.**

## Features
- Dashboard with live document, unique-term, and posting statistics
- Add and delete text documents
- Text normalization and tokenization
- Stop-word filtering
- Inverted index viewer (term → document IDs)
- Search with a simple TF-IDF-inspired ranking score
- Demo documents included
- Responsive red-and-black interface

## Run locally (Windows / macOS)
1. Install Python 3.10+ and VS Code.
2. Extract this ZIP.
3. Open the extracted `SAMRISE_SEARCH_INDEXER` folder in VS Code.
4. Open Terminal → New Terminal.
5. Create a virtual environment:
   - Windows: `python -m venv venv` then `venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
6. Install packages: `pip install -r requirements.txt`
7. Start the website: `python app.py`
8. Open `http://127.0.0.1:5000` in your browser.

## Project structure
```text
SAMRISE_SEARCH_INDEXER/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## How the indexer works
1. **Document input:** the user adds a title, category, and text.
2. **Tokenization:** text is converted to lowercase and split into words.
3. **Normalization:** punctuation is removed and common stop words are filtered.
4. **Index construction:** each unique word maps to the IDs of documents containing it.
5. **Query processing:** the search query goes through the same tokenizer.
6. **Retrieval and ranking:** matching documents are scored using a small TF-IDF-inspired formula and sorted by score.

## Deploy on GitHub + Render
1. Create a GitHub repository.
2. Upload the contents of this folder. Keep `templates` and `static` as folders at the repository root.
3. On Render, create **New → Web Service** and connect the repository.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Choose a free instance if available and deploy.

## Academic note
This is a learning prototype. Its documents and index are stored in memory, so newly added documents reset when the server restarts. It is not a production search engine and does not fetch or crawl external websites.
