from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage, SystemMessage
from typing import Annotated
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
import os
from langchain_tavily import TavilySearch

load_dotenv('.env')
config = dotenv_values(".env")









@tool
def tavily_search(query: str, allowed_websites: list[str] = []) -> dict:
    """
    Perform a web search using Tavily Search API.
    Can be restricted to specific websites provided.
    Is used when the chatbot needs to look up information. Unless otherwise, stick to the allowed sites only.
    You should priotize these sites over others.Just incase the sites have no results, you can go ahead and use other sites. 
    Only and only if they have no results. What you dont know say I don't know. Do not make up answers. 
    Do not answer questions that are not related to Ugandan agricultural business. Be precise and accurate in your answers.
      Neither too long nor too short answers.
    """
    
    tavily_tool = TavilySearch(max_results=3)

   
    return tavily_tool.invoke({"query": query, "site_filter": allowed_websites})
    
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] 

llm = ChatGroq(model=config["GROQ_MODEL"],api_key=config["GROQ_API_KEY"])         
llm_with_tools = llm.bind_tools([tavily_search])


def chatbot(state: State) -> State:
    messages = state["messages"] 
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tool(state: State) -> State:
    """
    Call the appropriate tool as requested by the LLM. 
    Do not execute any tool calls directly in the chatbot function.
    Return the result of the tool call to the chatbot node.
    """
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        raise ValueError("No tool calls found in the last message.")
    
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    if tool_name == "tavily_search":
        result = tavily_search.invoke(tool_args)
        return {"messages": [ToolMessage(content=str(result), tool_call_id=tool_call["id"])]}
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
    
def should_continue(state: State) -> str:
    """
    Route the graph based on the LLM's response.
    If the last message contains a tool call, route to the call_tool node.
    Otherwise, end the conversation.
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tool"
    else:
        return END

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)


graph_builder.add_node("call_tool", call_tool)



graph_builder.add_edge(START, "chatbot")

 


graph_builder.add_conditional_edges("chatbot", should_continue, {
    "call_tool": "call_tool",
    END: END
})

graph_builder.add_edge("call_tool", "chatbot")






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
    
    print("Welcome to the Ugandan Agricultural Traders Business Assistant")
    print("You can now ask any question related to Agriculture.")
   
    for site in allowed_sites:
        print(f"Allowed site: {site}")
                

        
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye")
            break
        
        user_message = HumanMessage(content=user_input, 
                                    additional_kwargs={"allowed_websites": allowed_sites})
        
        system_message = SystemMessage(content="You are a helpful assistant that provides accurate information about Ugandan agricultural business. Use the Tavily Search tool to look up information.")


        
        try:
            for s in graph.stream({"messages": [system_message, user_message]}):
                if "__end__" in s:
                    final_state = s["__end__"]
                    if final_state["messages"]:
                        print(f"Chatbot: {final_state['messages'][-1].content}")
                else:
                    print(f"Intermediate State: {s}")

        except Exception as e:
            print(f"Error happened: {e}")
