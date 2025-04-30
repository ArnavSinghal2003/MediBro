from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image, lang="eng+spa+tel+hin+tam+mal")

def translate_text(text, target_lang):
    return GoogleTranslator(source="auto", target=target_lang).translate(text)
