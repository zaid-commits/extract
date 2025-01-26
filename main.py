from flask import Flask, request, render_template, redirect, url_for, jsonify
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

extracted_text = ""

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
    full_prompt = f"{extracted_text}\n\n{prompt}"
    response = model.generate_content(full_prompt)
    print("Gemini API response:", response)  # Add this line to log the response
    return response.text

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file.save(file.filename)
            text = extract_text_from_pdf(file.filename)
            return render_template('chat.html', text=text)
    return render_template('upload.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    print("User input:", user_input)  # Add this line to log the user input
    response_text = get_gemini_response(user_input)
    print("Response text:", response_text)  # Add this line to log the response text
    return jsonify({'response': response_text})

if __name__ == "__main__":
    app.run(debug=True)