

import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction





persistent_directory = "chroma_db"
def create_vector_store(urls: list[str]):


    loader = WebBaseLoader(urls)
    documents = loader.lazy_load()


    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)




    embeddings = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(
        docs,
        embedding=embeddings,
        persist_directory=persistent_directory,
    )

    
    if __name__ == "__main__":
        allowed_sites = [
             "ura.go.ug",
        "ursbs.go.ug",
        "ugandaexports.go.ug",
        "ugandagrainscouncil.org",
            "eagc.org",
            "ugandainvest.go.ug",
            "unbs.go.ug",
            "agriculture.go.ug"
        ]

    

    
    relevant_docs = create_vector_store(allowed_sites)
    print(f"Number of relevant documents found: {len(relevant_docs)}")

