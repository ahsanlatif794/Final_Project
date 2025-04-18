
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter # Importing text splitter from Langchain
from langchain.schema import Document # Importing Document schema from Langchain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import shutil

load_dotenv()
CHROMA_PATH = "chroma"
def load_documents(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
    for filename in os.listdir(folder_path):
    # Create full path for each file in the folder
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):        # Check if it's a file (not a directory)
            ext = os.path.splitext(filename)[1].lower()
            print(f"Processing file: {file_path}, Extension: {ext}")
  
            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif ext == ".docx":
                loader = Docx2txtLoader(file_path)
            else:
                print(f"Unsupported file type: {ext}")
                continue
            documents.extend(loader.load())
 
    return documents # Load PDF documents and return them as a list of Document objects

#####################################SPLIT TEXT FUNCTION###############################################33
def split_text(documents: list[Document]):
  # Initialize text splitter with specified parameters
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300, # Size of each chunk in characters
    chunk_overlap=100, # Overlap between consecutive chunks
    length_function=len, # Function to compute the length of the text
    add_start_index=True, # Flag to add start index to each chunk
  )

  # Split documents into smaller chunks using text splitter
  chunks = text_splitter.split_documents(documents)
  print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
 

  return chunks # Return the list of split text chunks
######################################SAVE_TO_FASISS_VECTOR_DATASTORE###################################################3
def save_to_faiss(chunks: list[Document]):
    if not chunks:
        print("No chunks to process")
        return None

    # 1. Clear existing FAISS files
    FAISS_PATH = "faiss_index"
    if os.path.exists(FAISS_PATH):
        for file in os.listdir(FAISS_PATH):
            os.remove(os.path.join(FAISS_PATH, file))
    else:
        os.makedirs(FAISS_PATH)

    # 2. Process all chunks at once
    try:
        print(f"Creating FAISS index with {len(chunks)} chunks...")
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Single operation to create and save index
        faiss_index = FAISS.from_documents(
            documents=chunks,
            embedding=embedding_model
        )
        
        # Save the complete index
        faiss_index.save_local(FAISS_PATH)
        return FAISS_PATH

    except Exception as e:
        print(f"Error: {str(e)}")
        if os.path.exists(FAISS_PATH):
            shutil.rmtree(FAISS_PATH)
        return None
                
def generate_data_store(file_paths):
  documents = load_documents(file_paths) # Load documents from a source
  chunks = split_text(documents) # Split documents into manageable chunks
  db_path = save_to_faiss(chunks) # Save the processed data to a data store
  return db_path

#---------------------------------- Manage Chat history---------------------------------
chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def manage_history(history):
    for i in range(0,len(history),2):
        user_message = history[i].get("message", "") 
        if i + 1 < len(history):  # Safe check
            assistant_message = history[i + 1].get("message", "") 
        else:
            assistant_message = ""  # Or skip this round

        chat_history.save_context(
            {"input" : user_message},
            {"output":assistant_message }
        )
    return chat_history
#---------------------------------- Validate current query---------------------------------
def is_current_event_query(query: str) -> bool:
    """
    Heuristic to check if the query is about current events.
    """
    current_keywords = [
        "today", "latest", "current", "now", "update", "happening", 
        "news", "recent", "ongoing", "breaking", "2024", "2025"
    ]
    return any(word in query.lower() for word in current_keywords)
# ---------------------------------Finding source---------------------
def response_with_sources(result):
    answer = result['result']
    sources = result['source_documents']
    
    source_info = "\n\nSources:"
    for doc in sources:
        source = doc.metadata.get('source', 'Unknown source')
        page = doc.metadata.get('page', 'N/A')
        source_info += f"\n- {source} (Page {page})"
    
    return answer + source_info
