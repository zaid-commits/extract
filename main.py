from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

extracted_text = ""
conversation_history = []

def extract_text_from_pdf(pdf_path):
    global extracted_text
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        extracted_text = text
        return text

def get_gemini_response(prompt):
    global conversation_history
    line_count = len(extracted_text.splitlines())  #len count 
    context = (
        "You are an AI assistant helping with PDF content extraction and analysis. Your name is ImpicAI, trained by Zaid Rakhange "
        "at Impic. Impic is a tech community for developers, freelancers, and tech enthusiasts. The community link is "
        "https://community.impic.tech. When referencing information from the PDF, include a citation indicating the page number "
        "in the format [Page X](#page=X), so that the UI can link to that area.\n"
        f"The PDF has {line_count} lines. do not give any answer other than the context saved "
        f"also tell the number of images present as per the extracted text. "
    )
    conversation_history.append(f"User: {prompt}")
    full_prompt = (
        f"{context}\n\nExtracted Text:\n{extracted_text}\n\nConversation History:\n" + "\n".join(conversation_history)
    )
    response = model.generate_content(full_prompt)
    print("Gemini API response:", response)  # Log the response
    ai_response = response.text
    ai_response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', ai_response)  
    ai_response = re.sub(r'<b>(.*?)</b>\*', r'<b>\1</b>\n', ai_response)  
    conversation_history.append(f"ImpicAI: {ai_response}")
    return ai_response

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global conversation_history
    conversation_history = []  
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            text = extract_text_from_pdf(file_path)
            return render_template('chat.html', text=text, pdf_path=file.filename)
    return render_template('upload.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    print("User input:", user_input)  
    response_text = get_gemini_response(user_input)
    print("Response text:", response_text)  
    return jsonify({'response': response_text})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('../uploads', filename)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)