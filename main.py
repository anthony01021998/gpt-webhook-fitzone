from flask import Flask, request
import openai
import os, requests

app = Flask(__name__)

VERIFY_TOKEN = "fitzone2025"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook GPT for FITZONE is online!"

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

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên viên tư vấn gói tập cao cấp tại phòng gym FITZONE. Trả lời chuyên nghiệp, ngắn gọn, dễ hiểu."},
                    {"role": "user", "content": message}
                ]
            )
            answer = response["choices"][0]["message"]["content"].strip()

            # Gửi lại message qua Messenger
            url = "https://graph.facebook.com/v17.0/me/messages"
            params = {"access_token": PAGE_ACCESS_TOKEN}
            headers = {"Content-Type": "application/json"}
            payload = {
                "recipient": {"id": sender_id},
                "message": {"text": answer}
            }
            requests.post(url, params=params, headers=headers, json=payload)

            return "ok", 200
        except Exception as e:
            print("❌ Lỗi:", e)
            return "error", 500
