from flask import Flask, render_template, request, jsonify
from collections import defaultdict
import re
import math

app = Flask(__name__)

# Demo data makes the project useful immediately after launch.
documents = [
    {"id": 1, "title": "Introduction to Artificial Intelligence", "category": "Technology",
     "content": "Artificial intelligence enables machines to learn reason and solve problems. Machine learning is an important part of AI."},
    {"id": 2, "title": "Python Programming Basics", "category": "Programming",
     "content": "Python is a beginner friendly programming language used for web development data science and artificial intelligence."},
    {"id": 3, "title": "How Search Engines Work", "category": "Computer Science",
     "content": "A search engine indexer processes documents tokenizes text and builds an inverted index for fast information retrieval."},
    {"id": 4, "title": "The World Wide Web", "category": "Internet",
     "content": "The web connects information through websites links browsers servers and search systems."},
]

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
    "to", "of", "in", "on", "for", "with", "as", "by", "at", "from", "this",
    "that", "it", "its", "into", "about", "their", "they", "them", "we", "you"
}

def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]

def build_index():
    index = defaultdict(list)
    for doc in documents:
        words = tokenize(doc["title"] + " " + doc["content"])
        for word in set(words):
            index[word].append(doc["id"])
    return dict(index)

def search_documents(query):
    terms = tokenize(query)
    if not terms:
        return []
    index = build_index()
    total_docs = max(len(documents), 1)
    scores = defaultdict(float)
    for term in terms:
        matches = index.get(term, [])
        if not matches:
            continue
        # Simple TF-IDF-inspired score: rarer terms carry more weight.
        idf = math.log(1 + total_docs / (1 + len(matches)))
        for doc_id in matches:
            doc = next((d for d in documents if d["id"] == doc_id), None)
            if not doc:
                continue
            title_words = tokenize(doc["title"])
            body_words = tokenize(doc["content"])
            tf = title_words.count(term) * 2 + body_words.count(term)
            scores[doc_id] += (1 + math.log(1 + tf)) * idf
    results = []
    for doc_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True):
        doc = next(d for d in documents if d["id"] == doc_id)
        snippet = doc["content"][:190] + ("…" if len(doc["content"]) > 190 else "")
        results.append({**doc, "score": round(score, 3), "snippet": snippet})
    return results

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    index = build_index()
    return jsonify({
        "documents": len(documents),
        "terms": len(index),
        "postings": sum(len(ids) for ids in index.values()),
        "avg_terms": round(sum(len(tokenize(d["content"])) for d in documents) / max(len(documents), 1))
    })

@app.route("/api/index")
def get_index():
    index = build_index()
    return jsonify([{"term": term, "documents": ids, "frequency": len(ids)}
                    for term, ids in sorted(index.items())])

@app.route("/api/documents", methods=["GET", "POST"])
def docs():
    if request.method == "GET":
        return jsonify(documents)
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    category = (data.get("category") or "General").strip() or "General"
    if not title or not content:
        return jsonify({"error": "Please provide both a title and document content."}), 400
    new_id = max([d["id"] for d in documents], default=0) + 1
    documents.append({"id": new_id, "title": title, "category": category, "content": content})
    return jsonify({"message": "Document added and indexed.", "document": documents[-1]})

@app.route("/api/documents/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    global documents
    before = len(documents)
    documents = [d for d in documents if d["id"] != doc_id]
    if len(documents) == before:
        return jsonify({"error": "Document not found."}), 404
    return jsonify({"message": "Document removed from the index."})

@app.route("/api/search")
def search():
    query = request.args.get("q", "")
    return jsonify({"query": query, "results": search_documents(query), "terms": tokenize(query)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
