import os

from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


load_dotenv()


current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db")

def create_vector_store():


    loader = WebBaseLoader(urls)
    documents = loader.load()


    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)




    embeddings = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    if not os.path.exists(persistent_directory):
        print(f"\n--- Creating vector store in {persistent_directory} ---")
        db = Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
        print(f"--- Finished creating vector store in {persistent_directory} ---")
    else:
        print(f"Vector store {persistent_directory} already exists. No need to initialize.")
        db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)


    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )


    

    
    relevant_docs = retriever.invoke(query)

