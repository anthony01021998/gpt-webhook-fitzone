
from flask import Flask, request
from openai import OpenAI
import os, requests

app = Flask(__name__)

VERIFY_TOKEN = "fitzone2025"  # bạn có thể thay bằng token riêng

# Khởi tạo client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook GPT for FITZONE is online!"

def send_message(sender_id, message_text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }
    requests.post(url, params=params, headers=headers, json=payload)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        return (challenge, 200) if token == VERIFY_TOKEN else ("❌ Xác minh thất bại", 403)

    elif request.method == "POST":
        try:
            data = request.get_json()
            message = data['entry'][0]['messaging'][0]['message']['text']
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']

            # Gọi GPT để tạo phản hồi
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên viên tư vấn gói tập cao cấp tại phòng gym FITZONE. Trả lời chuyên nghiệp, ngắn gọn, dễ hiểu."},
                    {"role": "user", "content": message}
                ]
            )
            answer = response.choices[0].message.content.strip()
            send_message(sender_id, answer)
            return "ok", 200

        except Exception as e:
            print("❌ Lỗi:", e)
            return "error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
=======
from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response["choices"][0]["message"]["content"]
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)
