from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

# הכנסת מפתח API של Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyAoTsd6CAYNgTrsAwCHIBx53ge2CeRY-FE"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    instructions = data.get("instructions", "אתה עוזר אישי בתוך מערכת סינון תכנים, תענה בעברית פשוטה ולעניין.")

    if not prompt:
        return jsonify({"reply": "אין שאלה."})

    try:
        full_prompt = f"{instructions}\n\n{prompt}"
        response = model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": 500}
        )

        if hasattr(response, "text"):
            reply = response.text.strip()
        elif hasattr(response, "parts") and response.parts:
            reply = response.parts[0].text.strip()
        else:
            reply = "לא התקבלה תשובה מהמודל."

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"שגיאה: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
