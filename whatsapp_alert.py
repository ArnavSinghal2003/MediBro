import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from flask_api import send_whatsapp_message

# Load environment variables
load_dotenv()

app = Flask(__name__)

# UltraMsg API Credentials
ULTRAMSG_INSTANCE_ID = os.getenv("INSTANCE_ID")  # UltraMsg instance ID
ULTRAMSG_TOKEN = os.getenv("TOKEN")  # UltraMsg API token
WHATSAPP_NUMBER = os.getenv("RECEIVER_PHONE")  # Recipient's WhatsApp number

# Function to send WhatsApp message
def send_whatsapp_alert(message):
    url = f"http://api.textmebot.com/send.php?recipient=+918920844767&apikey=H27wXcUnhJNq&text=This%20is%20a%20test"
    
    payload = {
        "token": os.getenv("TOKEN"),  # API token from .env
        "to": os.getenv("RECEIVER_PHONE"),  # Recipient's WhatsApp number
        "body": message,
    }

    response = requests.post(url, json=payload)
    return response.json()  # Return the response for debugging

# API Route to trigger WhatsApp alert
@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    message = data.get("message", "No message provided")

    response = send_whatsapp_message(message)
    
    return jsonify({
        "message_sent": message,
        "ultramsg_response": response,
        "status": "success" if response.get("sent") else "failed"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
