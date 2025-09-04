import streamlit as st
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import os 
import dotenv
import ast
from node import graph, State, allowed_sites

dotenv.load_dotenv()

st.title("eMaisha Pay Agricultural Traders Business Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    

    

    if isinstance(message, AIMessage) and not message.tool_calls:
        with st.chat_message("assistant"):
            st.markdown(message.content)
        
    elif isinstance(message, AIMessage) and message.tool_calls:
        with st.chat_message("assistant"):
            st.markdown("Thinking...")

            with st.expander("Tool Call"):
                st.json(message.tool_calls)

    elif isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content) 

    elif isinstance(message, ToolMessage):
        with st.chat_message("tool"):
            st.markdown("Fetching results...")

            with st.expander("Search Results"):
                try:
                    content = ast.literal_eval(message.content)
                    st.json(content)
                except (ValueError, SyntaxError):
                    st.markdown(message.content)    

if prompt := st.chat_input("Ask a question about Ugandan agricultural business...."):

    
    
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    initial_state = {
        "messages": [HumanMessage(content=prompt, additional_kwargs={"allowed_sites":allowed_sites})]
    }

    with st.spinner("Processing..."):
       

        for s in graph.stream(initial_state):
            for key, value in s.items():
                if isinstance(value, dict) and "messages" in value:
                    new_messages = value["messages"]
                    for new_msg in new_messages:
                        if new_msg not in st.session_state.messages:
                            st.session_state.messages.append(new_msg)



    st.rerun()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    

    
    