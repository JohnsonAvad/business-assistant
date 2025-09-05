import os 
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


@tool
def tavily_search(query: str, allowed_websites: list[str] = []) -> dict:
    """
    Perform a web search using Tavily Search API.
    Can be restricted to specific websites provided.
    Is used when the chatbot needs to search the websites. Unless otherwise, stick to the allowed sites only.
    You should priotize these sites over others.Just incase the sites have no results, you can go ahead and use other sites. 
    Only and only if they have no results. You are to return urls of the top relevant websites only based on the query.
    Your answers should only be urls 
    Do not answer questions that are not related to Ugandan agricultural business.

    """
    
    tavily_tool = TavilySearch(max_results=3)

   
    return tavily_tool.invoke({"query": query, "site_filter": allowed_websites, "include_urls": True})

@tool
def database_lookup(query: str) -> str:
    """
    Look up information in the local vector database(ChromaDB).
    This tool should be called first before the tavily search tool.
    It takes a query string as input and returns relevant text chunks from the database.
    If no relevant documents are found, it returns a message indicating so.
    """
    persistent_directory = "chroma_db"
    embeddings = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    db = Chroma(
        persist_directory=persistent_directory,
        embedding_function=embeddings
    )
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    relevant_docs = retriever.invoke(query)
    if not relevant_docs:
        return "No relevant documents found in the database."
    
    return "\n\n".join([doc.page_content for doc in relevant_docs])