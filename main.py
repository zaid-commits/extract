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
    context = "You are an AI assistant helping with PDF content extraction and analysis. Your name is ImpicAI, trained by Zaid Rakhange at Impic. Impic is a tech community for developers, freelancers, and tech enthusiasts. The community link is https://community.impic.tech, "
    conversation_history.append(f"User: {prompt}")
    full_prompt = f"{context}\n\nExtracted Text:\n{extracted_text}\n\nConversation History:\n" + "\n".join(conversation_history)
    response = model.generate_content(full_prompt)
    print("Gemini API response:", response)  # Log the response
    ai_response = response.text
    ai_response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', ai_response)  # Make bold words
    ai_response = re.sub(r'<b>(.*?)</b>\*', r'<b>\1</b>\n', ai_response)  # New line and remove asterisk
    conversation_history.append(f"ImpicAI: {ai_response}")
    return ai_response

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global conversation_history
    conversation_history = []  # Reset conversation history when a new file is uploaded
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
    print("User input:", user_input)  # Log the user input
    response_text = get_gemini_response(user_input)
    print("Response text:", response_text)  # Log the response text
    return jsonify({'response': response_text})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('../uploads', filename)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)