import streamlit as st
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
import os
import dotenv
import ast
from main import graph, State, allowed_sites
import time

dotenv.load_dotenv()

st.title("eMaisha Pay Agricultural Traders Business Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)

    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

    elif isinstance(message, ToolMessage):
        pass


if prompt := st.chat_input("Ask a question about Ugandan agricultural business...."):

    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.status("Thinking...", expanded=True) as status:
        initial_state = {
            "messages": [
                SystemMessage(
                    content="You are a helpful assistant that provides accurate information about Ugandan agricultural business. "
                ),
                HumanMessage(
                    content=prompt, additional_kwargs={"allowed_sites": allowed_sites}
                ),
            ]
        }

        def get_stream():
            last_message_content = ""

            for s in graph.stream(initial_state):
                for key, value in s.items():
                    if key == "chatbot":
                        final_response_message = value["messages"][-1]
                        last_message_content = final_response_message.content
                        yield final_response_message
                    elif key == "check_db":
                        status.write(
                            "Checking database for relevant stored information..."
                        )
                    elif key == "search_web":
                        status.write("Searching the web for relevant information...")

        with st.chat_message("assistant"):
            st.write_stream(get_stream())

    st.rerun()

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
