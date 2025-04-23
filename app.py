# app.py

import re
from flask import Flask, request, jsonify, send_from_directory
from data_loader import load_faq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)

# Serve the chat UI
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

# 1) Load the FAQ entries
faq_entries = load_faq()

# 2) Build TF–IDF matrix over the questions
questions  = [e["question"] for e in faq_entries]
vectorizer = TfidfVectorizer(stop_words="english")
faq_matrix = vectorizer.fit_transform(questions)

# 3) Regex to pull out “CSE ####”
COURSE_RE = re.compile(r"\bCSE\s?(\d{4})\b", re.IGNORECASE)

# 4) Map common course‑name synonyms → course codes
SYNONYMS = {
    "data structures": "CSE 2050",
    # add more mappings if needed
}

@app.route("/faqs", methods=["GET"])
def list_faqs():
    """Return the full list of FAQs as JSON."""
    return jsonify(faq_entries)

@app.route("/ask", methods=["POST"])
def ask():
    """Return the best‐matching FAQ entry for a user question."""
    payload = request.get_json(force=True)
    user_q  = payload.get("question", "").strip()
    lower_q = user_q.lower()

    # 0) Name‑based override (e.g. "data structures")
    for name, code in SYNONYMS.items():
        if name in lower_q:
            for entry in faq_entries:
                if code.lower() in entry["question"].lower():
                    return jsonify(entry)

    # 1) Course‑code override (e.g. CSE 2050)
    m = COURSE_RE.search(user_q)
    if m:
        code = f"CSE {m.group(1)}"
        for entry in faq_entries:
            if code.lower() in entry["question"].lower():
                return jsonify(entry)

    # 2) TF–IDF fallback
    q_vec     = vectorizer.transform([user_q])
    sims      = linear_kernel(q_vec, faq_matrix).flatten()
    best_idx  = sims.argmax()
    best_score = sims[best_idx]

    # If similarity is too low, apologize
    if best_score < 0.2:
        return (
            jsonify({
                "id": None,
                "question": user_q,
                "answer": "Sorry, I don't know the answer to that yet."
            }),
            404
        )

    return jsonify(faq_entries[best_idx])

if __name__ == "__main__":
    # Run on 5001 to avoid macOS port conflicts
    app.run(debug=True, port=5001)
