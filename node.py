from dotenv import dotenv_values
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage
from typing import Annotated
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain_tavily import TavilySearch


config = dotenv_values('.env')

os.environ["TAVILY_API_KEY"] = config["TAVILY_SEARCH_API_KEY"]

llm = ChatGroq(model=config["GROQ_MODEL"],api_key=config["GROQ_API_KEY"]) 


def get_tavily_tool(max_results=2):
    return TavilySearch(max_results=max_results) 

tavily_tool = get_tavily_tool()
tools = [tavily_tool]


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] 
    search_query: str = None
    allowed_sites: list[str] = []
    search_results: dict = None 

graph_builder = StateGraph(State)
 
def tavily_search(state: State) -> State:
    query = state.search_query
    websites = state.allowed_sites

    if not query:
        
        return {"search_results":"No query provided"}
    
    if not websites:
       
        return {"search_results" : tavily_tool.invoke(query)}
    
    all_results = {}
    for site in websites:
        site_query = f"{query} site:{site}"
        result = tavily_tool.invoke(site_query)
        all_results[site] = result

     
    return {"search_results": all_results} 

def chatbot(state: State) -> State:
    messages = state.messages
    response = llm.invoke(messages)
    return State(messages=add_messages(messages, [response]))

graph_builder.add_node("chatbot",chatbot)


graph_builder.add_node("web_search",tavily_search)



graph_builder.add_edge(START, "web_search")

 


def should_continue(state: State) -> str:
    if state.search_results is not None:
        return "chatbot"

    else:
        return END  

graph_builder.add_conditional_edges(
    "web_search",
    should_continue,
    {"chatbot": "chatbot", END: END}



)      


graph = graph_builder.compile()

allowed_sites=[
        "ura.go.ug",
        "ursbs.go.ug",
        "ugandaexports.go.ug",
        "ugandagrainscouncil.org",
            "eagc.org",
            "ugandainvest.go.ug",
            "unbs.go.ug",
            "agriculture.go.ug"
    ] 

if __name__ == "__main__":
    # current_state_state = State(messages=[])
    print("Welcome to the Ugnadan Agricultural Traders Business Assistant")
    print("You can now ask any question related to Agriculture.")
   
    for site in allowed_sites:
        print(f"Allowed site: {site}")
                

        
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye")
            break
        current_state = State(
        messages = [HumanMessage(content="Hello, how are you?")],
        search_query=user_input, 
        allowed_sites=allowed_sites 

        )
        chatbot_reply = graph.invoke(current_state)
        print(f"Chatbot: {chatbot_reply}")

