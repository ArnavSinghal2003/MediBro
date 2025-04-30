from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Function to send WhatsApp message using TextMeBot
def send_whatsapp_message(message, phone_number):
    try:
        url = f"http://api.textmebot.com/send.php?recipient={phone_number}&apikey=H27wXcUnhJNq&text={message}"
        response = requests.post(url)
        print("Whatsapp API Response:", response.text)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

# Flask route to trigger message
@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    prescription_text = data.get("prescription_text", "").strip()
    phone_number = data.get("phone_number", "").strip()

    if not prescription_text:
        return jsonify({"status": "failed", "message": "Prescription text is empty!"}), 400
    if not phone_number.startswith("+"):
        return jsonify({"status": "failed", "message": "Invalid phone number!"}), 400

    full_message = f"💊 Prescription Alert:\n{prescription_text}"
    response = send_whatsapp_message(full_message, phone_number)

    return jsonify({
        "status": "success",
        "message_sent": full_message,
        "api_response": response
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
