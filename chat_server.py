import os
import uuid
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# הכנסת מפתח API של Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyAoTsd6CAYNgTrsAwCHIBx53ge2CeRY-FE"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

VIDEO_FOLDER = "C:/xaxa_browser/srton"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    instructions = data.get("instructions", "אתה עוזר אישי בתוך מערכת סינון תכנים, תענה בעברית פשוטה ולעניין.")

    if not prompt:
        return jsonify({"reply": "אין שאלה."})

    # בדיקה אם המשתמש שלח קישור לבדיקה
    if prompt.startswith("בדוק: ") and "youtube.com/watch" in prompt:
        url = prompt.split("בדוק: ")[-1].strip()
        try:
            video_id = str(uuid.uuid4())
            output_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")
            command = [
                "yt-dlp",
                "-f", "best[ext=mp4]",
                "-o", output_path,
                url
            ]
            subprocess.run(command, check=True)
            return jsonify({"reply": f"הסרטון נשמר בהצלחה: {output_path}"})
        except Exception as e:
            return jsonify({"reply": f"שגיאה בהורדת הסרטון: {str(e)}"})

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
