import streamlit as st
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import uuid
import os 
import dotenv
import ast
from node import graph, State, allowed_sites

dotenv.load_dotenv()

st.title("Business Assistant Chatbot")

if "state" not in st.session_state:
    st.session_state.state  = {"messages": [],"thread_id":str
                                      (uuid.uuid4())}
    
for message in st.session_state.state["messages"]:
    message: BaseMessage

    Toolcall = "This message is a tool call. "

    if isinstance(message, AIMessage) and not message.content:
        with st.chat_message(message.type):
            st.markdown(Toolcall)
        
    elif isinstance(message, ToolMessage):
        with st.chat_message(message.type):
            with st.expander("Tool Call"):
                content = message.content
                content = ast.literal_eval(content)
                st.markdown(content)

    else:
        with st.chat_message(message.type):
            st.write(message.content) 

if prompt := st.chat_input("Ask a question"):
    new_msg = HumanMessage(content=prompt)
    
    st.session_state.state["messages"].append(new_msg)
    state = State(
        messages=st.session_state.state["messages"],
        search_query=prompt,
        allowed_sites=allowed_sites,
        
    )

    with st.spinner("Thinking..."):
       result = graph.invoke(state)
      
    #    st.rerun