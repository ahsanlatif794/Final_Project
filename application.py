from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv # Importing dotenv to get API key from .env file
from utils.functions import generate_data_store
from tools.agent import ask_agent
from utils.functions import manage_history
import os

application = Flask(__name__)
CORS(application)
load_dotenv()
secret_key = os.getenv('authenticationKey')

@application.route('/')
def printHomeRoute():
    return render_template('index.html')

@application.route('/create_embedding', methods=['POST'])
def create_embedding():
    headers = request.json
    file_paths = headers.get('files_paths', [])
    authenticationKey = headers.get('authenticationKey')

    if not authenticationKey:
        return jsonify({"error": "Authentication key not entered"})

    if not file_paths:
        return jsonify({"error": "NO file paths"})

    if (secret_key == authenticationKey):
      db_path = generate_data_store(file_paths)
      return jsonify({"message": "Embeddings created", "db_path": db_path})


@application.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        query = data.get('query')
        history = data.get('history') or []
        authenticationKey = data.get('authenticationKey')


        if not authenticationKey:
            return jsonify({"error": "Authentication key not entered"})

        if (secret_key != authenticationKey):
            return jsonify({"error": "You entered wrong authentication key."})
        
        if (secret_key == authenticationKey):
            chat_history = manage_history(history)
            response = ask_agent(query,chat_history)
            print(type(response))
            return jsonify({"response": str(response)})


    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error for debugging
        return jsonify({
        "error": "An unexpected error occurred",
        "details": str(e)  # Only include in development environment
        }), 500

 
if __name__ == '__main__':
   application.run(debug=True)