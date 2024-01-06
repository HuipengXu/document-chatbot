import os
import streamlit as st
from io import StringIO
import re
import sys
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar

import traceback


# Config
st.set_page_config(layout="wide", page_icon="💬", page_title="文档问答机器人 🤖")


# Title
st.markdown(
    """
    <h2 style='text-align: center;'>快问问你的文档吧 😁</h1>
    """,
    unsafe_allow_html=True,
)


# To be able to update the changes made to modules in localhost (press r)
def reload_module(module_name):
    import importlib
    import sys

    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]


history_module = reload_module("modules.history")
layout_module = reload_module("modules.layout")
utils_module = reload_module("modules.utils")
sidebar_module = reload_module("modules.sidebar")

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()


# Configure the sidebar
sidebar.show_options()

user_chat_api_key, user_embedding_api_key = utils.load_api_key()

if not user_chat_api_key or not user_embedding_api_key:
    layout.show_api_key_missing()
else:
    uploaded_file = utils.handle_upload(["pdf", "txt", "csv"])
    select_history_file = sidebar.show_browser_history()
    select_history_file = (
        None if select_history_file == "你的历史文件" else select_history_file
    )

    if uploaded_file or select_history_file:
        uploaded_file = uploaded_file or select_history_file
        # Initialize chat history
        history = ChatHistory()
        try:
            chatbot = utils.setup_chatbot(
                uploaded_file,
                st.session_state["model"],
                st.session_state["temperature"],
            )
            st.session_state["chatbot"] = chatbot

            if st.session_state["ready"]:
                # Create containers for chat responses and user prompts
                response_container, prompt_container = st.container(), st.container()

                with prompt_container:
                    # Display the prompt form
                    is_ready, user_input = layout.prompt_form()

                    # Initialize the chat history
                    history.initialize(uploaded_file)

                    # Reset the chat history if button clicked
                    if st.session_state["reset_chat"]:
                        history.reset(uploaded_file)

                    if is_ready:
                        # Update the chat history and display the chat messages
                        history.append("user", user_input)

                        output = st.session_state["chatbot"].conversational_chat(
                            user_input
                        )

                        history.append("assistant", output)

                history.generate_messages(response_container)

        except Exception as e:
            traceback.print_exc()
            st.error(f"Error: {str(e)}")
