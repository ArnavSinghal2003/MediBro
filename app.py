import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from gtts import gTTS
import base64
import requests
from deep_translator import GoogleTranslator
import re
import pyperclip
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ------------------------ CONFIG ------------------------
BACKEND_URL = "http://127.0.0.1:5000/send_alert"
LANG_CODE = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta"
}

st.set_page_config(
    page_title="💊 MediBro - Prescription Assistant",
    layout="centered"
)

# ------------------------ SIDEBAR ------------------------
with st.sidebar:
    st.title("🩺 MediBro Assistant")
    st.markdown("### 📋 How It Works")
    st.markdown("""
    1. 📝 Upload Prescription (PDF or Image)  
    2. 🌐 Choose Preferred Language  
    3. 📱 Enter WhatsApp Number  
    4. 🚀 Process & Listen + Get Alert
    """)
    st.markdown("---")
    uploaded_file = st.file_uploader("📎 Upload Prescription", type=["pdf", "jpg", "jpeg", "png"])
    selected_lang = st.selectbox("🌐 Choose Language", ["English", "Hindi", "Telugu", "Tamil"])
    phone_number = st.text_input("📱 WhatsApp Number", placeholder="+91XXXXXXXXXX")
    process_file_button = st.button("🚀 Analyze Prescription")
    st.markdown("---")

# ------------------------ MAIN TITLE ------------------------
st.title("💊 MediBro - AI Medication Management")
st.markdown("#### Upload your prescription for translation, audio, schedule detection, and WhatsApp alerts.")

# ------------------------ FUNCTIONS ------------------------

def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image, lang="eng+hin+tel+tam")

def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        st.warning(f"⚠️ Translation failed: {e}")
        return text

def generate_audio(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    audio_path = "output.mp3"
    tts.save(audio_path)
    with open(audio_path, "rb") as audio:
        audio_base64 = base64.b64encode(audio.read()).decode()
    return f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg"></audio>'

def extract_schedule(text):
    keywords = [
        "morning", "afternoon", "evening", "night",
        "before food", "after food", "empty stomach"
    ]
    matches = re.findall(r"\b(" + "|".join(keywords) + r")\b", text, re.IGNORECASE)
    return list(set([m.capitalize() for m in matches])) or ["No specific timing mentioned."]

def extract_dosage(text):
    matches = re.findall(r'\b\d+\s?(?:tablet|tab|capsule|ml|mg|drops|units)\b', text, re.IGNORECASE)
    return list(set(matches)) or ["No dosage info found."]

# ------------------------ MAIN LOGIC ------------------------
if process_file_button and uploaded_file:
    if not phone_number or not phone_number.startswith("+"):
        st.error("📵 Please enter a valid WhatsApp number with country code.")
    else:
        with st.spinner("⏳ Processing prescription..."):
            try:
                # Step 1: Extract Text
                if uploaded_file.name.endswith(".pdf"):
                    st.session_state.extracted_text = extract_text_from_pdf(uploaded_file)
                else:
                    st.session_state.extracted_text = extract_text_from_image(uploaded_file)

                # Check if extracted text exists
                if not st.session_state.extracted_text.strip():
                    st.warning("⚠️ No text found in the prescription. Try a clearer file.")
                    st.stop()

                # Step 2: Translate
                lang_code = LANG_CODE.get(selected_lang, "en")
                if selected_lang != "English":
                    translation_output = translate_text(st.session_state.extracted_text, LANG_CODE[selected_lang])
                    if translation_output and translation_output != st.session_state.extracted_text:
                        st.session_state.translated_text = translation_output
                    else:
                        st.warning("⚠️ Translation might have failed. Sending English text instead.")
                        st.session_state.translated_text = st.session_state.extracted_text
                else:
                    st.session_state.translated_text = st.session_state.extracted_text


                # Show Extracted Text
                st.subheader("📄 Extracted Prescription Text (from OCR)")
                st.code(st.session_state.extracted_text)

                # Show Translated Text
                st.subheader(f"📄 Translated Prescription Text ({selected_lang})")
                st.code(st.session_state.translated_text)

                # Copy Button
                if st.button("📋 Copy Translated Text"):
                    pyperclip.copy(st.session_state.translated_text)
                    st.toast("Text copied to clipboard!")

                # Dosage Info
                st.subheader("💊 Dosage Details")
                st.write("**Schedule:**", ", ".join(extract_schedule(st.session_state.translated_text)))
                st.write("**Dosage Units:**", ", ".join(extract_dosage(st.session_state.translated_text)))

                # Audio Playback
                st.subheader("🔈 Audio Guide")
                st.markdown(generate_audio(st.session_state.translated_text, lang_code), unsafe_allow_html=True)

                # WhatsApp Alert
                st.subheader("📲 Send WhatsApp Alert")
                response = requests.post(BACKEND_URL, json={
                    "prescription_text": st.session_state.translated_text,
                    "phone_number": phone_number
                })

                if response.status_code == 200:
                    st.success("✅ WhatsApp message sent successfully!")
                else:
                    st.error("⚠️ Failed to send WhatsApp message.")

                st.toast("🎉 Prescription processed successfully!", icon="✅")

            except Exception as e:
                st.error(f"❌ Something went wrong: {e}")
                st.toast("❌ Error processing the file. Please try again.", icon="❌")
