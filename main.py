from dotenv import load_dotenv, dotenv_values

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage,
    SystemMessage,
)
from typing import Annotated
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
import os
from langchain_tavily import TavilySearch
from graph_tools import tavily_search, database_lookup

load_dotenv(".env")
config = dotenv_values(".env")


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatGroq(model=config["GROQ_MODEL"], api_key=config["GROQ_API_KEY"])
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
    tool_call_id = tool_call["id"]

    if tool_name == "tavily_search":
        result = tavily_search.invoke(tool_args)
        return {
            "messages": [ToolMessage(content=str(result), tool_call_id=tool_call["id"])]
        }
    elif tool_name == "database_lookup":
        result = database_lookup.invoke(tool_args["query"])
        return {
            "messages": [ToolMessage(content=str(result), tool_call_id=tool_call["id"])]
        }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def router(state: State) -> str:
    """
    Route the graph based on the LLM's response.
    If the last message contains a tool call, route to the call_tool node.
    Otherwise, end the conversation.
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        if tool_call["name"] == "database_lookup":
            return "check_db_results"
        elif tool_call["name"] == "tavily_search":
            return "search_web"
        else:
            return END

           
    else:
        return END


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)


graph_builder.add_node("check_db", call_tool)
graph_builder.add_node("search_web", call_tool)


graph_builder.add_edge(START, "chatbot")


graph_builder.add_conditional_edges(
    "chatbot", router, {"check_db": "check_db",
                        "search_web": "search_web",
                         END: END}
)

graph_builder.add_edge("check_db", "chatbot")
graph_builder.add_edge("search_web", "chatbot")


graph = graph_builder.compile()


allowed_sites = [
    "ura.go.ug",
    "ursbs.go.ug",
    "ugandaexports.go.ug",
    "ugandagrainscouncil.org",
    "eagc.org",
    "ugandainvest.go.ug",
    "unbs.go.ug",
    "agriculture.go.ug",
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

        user_message = HumanMessage(
            content=user_input, additional_kwargs={"allowed_websites": allowed_sites}
        )

        system_message = SystemMessage(
            content="You are a helpful assistant that provides accurate information about Ugandan"
            " agricultural business. Priotize using the database lookup tool to find answers in the local knowledge base. If that fails to produce relevant documents," \
            " you can then proceed to use the web search tool." 
            f"You can only search for information on the following websites: {allowed_sites}."
            " Use the Tavily Search tool to look up the most relevant urls by ranking." \
            "Do not answer questions that are not related to Ugandan agricultural business." \
            "Do not search outside the allowed sites unless there are no results from the allowed sites."
        )

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
