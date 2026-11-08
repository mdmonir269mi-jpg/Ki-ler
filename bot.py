import os
import time
import logging
import requests
from flask import Flask

# রেন্ডারের ওয়েব সার্ভিস পোর্ট রিকোয়ারমেন্ট পূরণের জন্য ফ্লাস্ক সার্ভার
app = Flask(__name__)

@app.route('/')
def home():
    return "NP Network OTP Gateway is Live & Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

logging.basicConfig(level=logging.INFO)

API_TOKEN = "NP-6HXU732PNEATGVFM"
BASE_URL = "https://www.npnetworkbd.cam/api/user"  # সঠিক ডোমেন সহ আপডেট করা হলো
TELEGRAM_BOT_TOKEN = "9168159119:AAFmg9tj8WKpvJ2mswXW5ipQjf3rQb0eZ7o"
GROUP_CHAT_ID = "-1004483895054"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Telegram error: {e}")

if __name__ == '__main__':
    import threading
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    logging.info("Starting NP Network OTP Background Worker...")
    
    seen_otps = set()
    while True:
        try:
            headers = {'mauthapi': API_TOKEN}
            res = requests.get(f"{BASE_URL}/success-otp", headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                otps = data.get('data', {}).get('otps', [])
                for item in otps:
                    msg = item.get('message', '')
                    num = item.get('number', '')
                    unique_key = f"{num}_{msg}"
                    if unique_key not in seen_otps:
                        seen_otps.add(unique_key)
                        if len(seen_otps) > 200:
                            seen_otps.pop()
                        
                        # টেলিগ্রাম গ্রুপে ওটিপি পাঠানো
                        text = f"⚡ <b>NP NETWORK - NEW OTP RECEIVED</b> ⚡\n━━━━━━━━━━━━━━━━━━━━━━\n📱 <b>Number:</b> <code>{num}</code>\n💬 <b>Message:</b> <i>{msg}</i>\n━━━━━━━━━━━━━━━━━━━━━━"
                        send_telegram_message(text)
        except Exception as err:
            logging.error(f"API Fetch Error: {err}")
        
        time.sleep(5)
