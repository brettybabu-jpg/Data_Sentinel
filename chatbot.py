from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from dotenv import load_dotenv

# 🔹 Load environment variables
load_dotenv()

# 🔹 Initialize Flask app
app = Flask(__name__)

# 🔹 Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 🔹 Load Knowledge Base
def load_kb():
    with open("kb.txt", "r", encoding="utf-8") as f:
        data = f.read().split("\n\n")
    qa_pairs = []
    for item in data:
        lines = item.split("\n")
        if len(lines) >= 2:
            keyword = lines[0].strip().lower()
            answer = lines[1].strip()
            qa_pairs.append((keyword, answer))
    return qa_pairs

kb = load_kb()

# 🔹 KB Search (fixed)
def search_kb(user_input):
    user_input = user_input.lower()

    for q, a in kb:
        if q in user_input:
            return a

    return None

# 🔹 Home route
@app.route("/")
def home():
    return render_template("index.html")

# 🔹 Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"].lower()

    # 🔹 GREETING
    if any(phrase in user_message for phrase in [
        "hi", "hello", "hey", "good morning", "good evening", "good afternoon"
    ]):
        return jsonify({
            "reply": "Hello! I'm DataSentinel. I can help you with database concepts like keys, constraints, and normalization. What would you like to know?"
        })

    # 🔹 EXIT
    if any(phrase in user_message for phrase in [
        "bye", "goodbye", "thank you", "thanks", "ok thanks"
    ]):
        return jsonify({
            "reply": "You're welcome! If you have more database questions later, feel free to ask. Goodbye!"
        })

    # 🔹 DATABASE KEYWORDS (FILTER)
    db_keywords = [
        "data","key","constraint","database","integrity","sql","table",
        "tuple","row","column","record","dbms","schema","normalization",
        "primary","foreign","null","join","transaction"
    ]

    # 🔹 BLOCK IRRELEVANT QUESTIONS
    if not any(word in user_message for word in db_keywords):
        return jsonify({
            "reply": "I can help with database topics like keys, constraints, tables, and SQL. Try asking something related to that."
        })

    # 🔹 CHECK KNOWLEDGE BASE
    kb_answer = search_kb(user_message)
    if kb_answer:
        return jsonify({"reply": kb_answer})

    # 🔹 AI FALLBACK
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
You are DataSentinel, a database assistant.

RULES:
- Answer only database-related questions.
- Keep answers short (2-3 lines).
- Be simple and human-like.
- Do NOT give long paragraphs.
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})


# 🔹 Run app
if __name__ == "__main__":
    app.run(debug=True)