from flask import Flask, request
from openai import OpenAI
import os
import requests

app = Flask(__name__)

# ===== 🔐 CẤU HÌNH =====
VERIFY_TOKEN = "fitzone2025"  # Token xác minh webhook từ Facebook
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # API Key OpenAI
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")    # Token Fanpage

# ===== ✅ KIỂM TRA SERVER ONLINE =====
@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook GPT for FITZONE is online!"

# ===== 📤 GỬI TIN NHẮN TRỞ LẠI MESSENGER =====
def send_message(sender_id, message_text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, params=params, headers=headers, json=payload)
    print("📤 Gửi về Messenger:", response.status_code, response.text)

# ===== 📬 XỬ LÝ WEBHOOK TỪ FACEBOOK =====
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "❌ Xác minh thất bại", 403

    elif request.method == "POST":
        try:
            data = request.get_json()
            print("📩 Nhận tin:", data)

            message = data['entry'][0]['messaging'][0]['message']['text']
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']

            # 🤖 Gửi prompt đến GPT
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là một chuyên viên tư vấn gói tập của phòng gym cao cấp tên là FITZONE. "
                            "Hãy trả lời khách hàng một cách chuyên nghiệp, ngắn gọn, rõ ràng và thuyết phục. "
                            "Luôn chủ động đưa ra lời khuyên và đề xuất các gói tập phù hợp."
                        )
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )

            answer = response.choices[0].message.content.strip()
            print("🤖 GPT trả lời:", answer)

            # 📤 Gửi lại cho khách
            send_message(sender_id, answer)

            return "ok", 200

        except Exception as e:
            print("❌ Lỗi xử lý webhook:", e)
            return "error", 500

# ===== 🚀 CHẠY SERVER =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
