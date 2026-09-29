import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT

load_dotenv()
app = Flask(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        history = data.get("history", [])
        if not message:
            return jsonify({"success": False, "error": "Please enter a message."}), 400

        context = []
        if isinstance(history, list):
            for item in history[-12:]:
                if isinstance(item, dict) and item.get("role") in ("user", "assistant"):
                    content = item.get("content", "")
                    if isinstance(content, str) and content.strip():
                        context.append(f"{item['role'].upper()}: {content}")

        prompt = f"""{SYSTEM_PROMPT}

Previous conversation:
{chr(10).join(context) if context else "(none)"}

Current user question:
{message}

Answer according to the IoT-only rules."""
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return jsonify({"success": True, "reply": response.text or "No response generated."})
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({"success": False, "error": "Something went wrong. Please check your API key and try again."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
