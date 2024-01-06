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
st.set_page_config(layout="wide", page_icon="💬", page_title="你的私人助理 🤖")


# Title
st.markdown(
    """
    <h2 style='text-align: center;'>快问问你的小助理吧 😁</h1>
    """,
    unsafe_allow_html=True,
)
st.divider()


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
sidebar.show_file_list()

user_chat_api_key, user_embedding_api_key = utils.load_api_key()

if not user_chat_api_key or not user_embedding_api_key:
    layout.show_api_key_missing()
else:
    uploaded_file = utils.handle_upload(["pdf", "txt", "csv"])

    # Initialize chat history
    history = ChatHistory()
    try:
        chatbot = utils.setup_chatbot(
            st.session_state["model"], st.session_state["temperature"], uploaded_file
        )
        st.session_state["chatbot"] = chatbot

        if st.session_state["ready"]:
            # Create containers for chat responses and user prompts
            response_container, prompt_container = st.container(), st.container()

            with prompt_container:
                # Display the prompt form
                is_ready, user_input = layout.prompt_form()

                # Initialize the chat history
                history.initialize()

                # Reset the chat history if button clicked
                if st.session_state["reset_chat"]:
                    history.reset()

                if is_ready:
                    # Update the chat history and display the chat messages
                    history.append("user", user_input)

                    output = st.session_state["chatbot"].conversational_chat(user_input)

                    history.append("assistant", output)

            history.generate_messages(response_container)

    except Exception as e:
        traceback.print_exc()
        st.error(f"Error: {str(e)}")
