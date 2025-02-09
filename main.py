from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

conversation_history = []

def get_flashcards(text):
    """
    Generates flashcards from the given text using Gemini API.
    """
    prompt = f"""
    Generate concise and structured flashcards from the following study material.
    The response should be in JSON format with an array of flashcards, 
    each containing 'question' and 'answer' keys.

    Example:
    {{
        "flashcards": [
            {{"question": "What is React?", "answer": "React is a JavaScript library for building UI."}},
            {{"question": "What is JSX?", "answer": "JSX is a syntax extension for JavaScript."}}
        ]
    }}

    Study Material:
    {text}
    """

    response = model.generate_content(prompt)
    
    print("Raw AI Response:", response.text)  # Debugging Output

    # Extract JSON from AI response
    try:
        # Find the JSON part in the response text
        start_index = response.text.find('{')
        end_index = response.text.rfind('}') + 1
        cleaned_response = response.text[start_index:end_index]
        
        flashcards = json.loads(cleaned_response)  # Converts AI output to Python dictionary
        return flashcards.get("flashcards", [])  # Extract only flashcards
    except (json.JSONDecodeError, ValueError) as e:
        print("Error parsing AI response:", str(e))
        return []

def get_chat_response(text):
    """
    Generates a chat response from the given text using Gemini API.
    """
    prompt = f"Respond to the following question:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

@app.route('/flashcards', methods=['POST'])
def flashcards():
    """
    API Endpoint to generate flashcards from user input.
    """
    data = request.json
    user_input = data.get("text", "")
    
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    flashcards = get_flashcards(user_input)

    return jsonify({"flashcards": flashcards, "response": "Here are your generated flashcards!"})

@app.route('/chat', methods=['POST'])
def chat():
    """
    API Endpoint to generate chat response from user input.
    """
    data = request.json
    user_input = data.get("text", "")
    
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    response_text = get_chat_response(user_input)

    return jsonify({"response": response_text})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)