from flask import Flask, request
from openai import OpenAI
import os, requests

app = Flask(__name__)

VERIFY_TOKEN = "fitzone2025"
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

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là một chuyên viên tư vấn gói tập của phòng gym cao cấp tên là FITZONE. "
                            "Trả lời khách hàng một cách chuyên nghiệp, rõ ràng, và thuyết phục."
                        )
                    },
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
