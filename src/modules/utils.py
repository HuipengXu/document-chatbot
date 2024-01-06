import os
import pandas as pd
import streamlit as st
import pdfplumber

from modules.openai_chatbot import Chatbot as GPTChatbot
from modules.baichuan_chatbot import Chatbot as BaichuanChatbot
from modules.embedder import Embedder


class Utilities:
    @staticmethod
    def handle_upload(file_types):
        """
        Handles and display uploaded_file
        :param file_types: List of accepted file types, e.g., ["csv", "pdf", "txt"]
        """
        uploaded_file = st.sidebar.file_uploader(
            "upload", type=file_types, label_visibility="collapsed"
        )
        st.session_state["reset_chat"] = True
        if uploaded_file is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander("Your CSV file :")
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Your PDF file :")
                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)

            def show_txt_file(uploaded_file):
                file_container = st.expander("Your TXT file:")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                file_container.write(content)

            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()

            file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            # if file_extension == ".csv" :
            #    show_csv_file(uploaded_file)
            if file_extension == ".pdf":
                show_pdf_file(uploaded_file)
            elif file_extension == ".txt":
                show_txt_file(uploaded_file)
        return uploaded_file

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or
        from the user's input and returns it
        """
        if not hasattr(st.session_state, "chat_api_key"):
            st.session_state.chat_api_key = None
        if not hasattr(st.session_state, "embedding_api_key"):
            st.session_state.embedding_api_key = None

        with st.sidebar.expander("🔑 API Key", expanded=True):
            user_chat_api_key = st.text_input(
                label="#### Input Chat API Key 👇",
                placeholder="sk-...",
                type="password",
            )
            user_embedding_api_key = st.text_input(
                label="#### Input Embedding API Key 👇",
                placeholder="sk-...",
                type="password",
            )
            if user_chat_api_key:
                st.session_state.chat_api_key = user_chat_api_key
            if user_embedding_api_key:
                st.session_state.embedding_api_key = user_embedding_api_key

        return user_chat_api_key, user_embedding_api_key

    @staticmethod
    def setup_chatbot(uploaded_file, model, temperature):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = Embedder()

        with st.spinner("Processing..."):
            if not isinstance(uploaded_file, str):
                uploaded_file.seek(0)
                file = uploaded_file.read()
                original_filename = uploaded_file.name
            else:
                file = uploaded_file
                original_filename = uploaded_file
            # Get the document embeddings for the uploaded file
            vectors = embeds.getDocEmbeds(file, original_filename)

            # Create a Chatbot instance with the specified model and temperature
            if model.startswith("gpt"):
                chatbot = GPTChatbot(model, temperature, vectors)
            elif model.startswith("baichuan"):
                chatbot = BaichuanChatbot(model, temperature, vectors)
        st.session_state["ready"] = True

        return chatbot
