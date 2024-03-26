import streamlit as st
from llama_index.core import VectorStoreIndex
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
import chromadb
import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv()

# Get Google API Key from environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Initialize HuggingFace embedding model
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

# Load documents from directory
loader = SimpleDirectoryReader(input_dir="./", required_exts=[".pdf"])
documents = loader.load_data()

# Initialize ChromaDB client
chroma_client = chromadb.EphemeralClient()

# Initialize Gemini LLM with Google API Key
llm = Gemini(api_key=GOOGLE_API_KEY)

# Initialize ChromaVectorStore and StorageContext
try:
    chroma_collection = chroma_client.create_collection("quickstart")
except chromadb.db.base.UniqueConstraintError as e:
    print("running except block")
    chroma_client.delete_collection("quickstart")
    chroma_collection = chroma_client.create_collection("quickstart")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
# Create VectorStoreIndex from documents
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, embed_model=embed_model
)
query_engine = index.as_query_engine(llm=llm)
# Function to perform query and display response
def perform_query(query):
    response = query_engine.query(query)
    return response

# Streamlit UI
st.title("Specialization Week FAQ Query System")

# Input for user query
query_input = st.text_input("Enter your query:")

# Button to trigger query
if st.button("Search"):
    if query_input:
        response = perform_query(query_input)
        st.write("Response:")
        st.write(response)
    else:
        st.write("Please enter a query.")
