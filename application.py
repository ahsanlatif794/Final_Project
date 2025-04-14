from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv # Importing dotenv to get API key from .env file
from utils.functions import generate_data_store
from tools.agent import ask_agent
from langchain.memory import ConversationBufferMemory
import os

application = Flask(__name__)
CORS(application)
load_dotenv()
secret_key = os.getenv('authenticationKey')

@application.route('/home')
def printHomeRoute():
    return 'Home Route'

@application.route('/create_embedding', methods=['POST'])
def create_embedding():
    headers = request.json
    file_paths = headers.get('files_paths', [])
    authenticationKey = headers.get('authenticationKey')

    if not authenticationKey:
        return jsonify({"error": "API KEY NOT ENTERED"})

    if not file_paths:
        return jsonify({"error": "NO file paths"})

    if (secret_key == authenticationKey):
      db_path = generate_data_store(file_paths)
      return jsonify({"message": "Embeddings created", "db_path": db_path})


@application.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data.get('query')
    history = data.get('history') or []
    authenticationKey = data.get('authenticationKey')

    chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    if not authenticationKey:
        return jsonify({"error": "API KEY NOT ENTERED"})

    if (secret_key == authenticationKey):
        for i in range(0,len(history),2):
            user_message = history[i].get("content", "") 
            assistant_message = history[i + 1].get("content", "") 
            chat_history.save_context(
                {"input" : user_message},
                {"output":assistant_message }
            )
    response = ask_agent(query,chat_history)
    return jsonify({"response": response})


 
if __name__ == '__main__':
   application.run(debug=True)