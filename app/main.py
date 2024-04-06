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
import sys

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
loader = SimpleDirectoryReader(input_dir="./", required_exts=[".pdf"])
documents = loader.load_data()
llm = Gemini(api_key=GOOGLE_API_KEY)
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, embed_model=embed_model
)
query_engine = index.as_query_engine(llm=llm)
def perform_query(query):
    response = query_engine.query(query)
    return response

st.title("Specialization Week FAQ Query System")

query_input = st.text_input("Enter your query:")

if st.button("Search"):
    if query_input:
        response = perform_query(query_input)
        st.write("Response:")
        st.write(response.response)
    else:
        st.write("Please enter a query.")
