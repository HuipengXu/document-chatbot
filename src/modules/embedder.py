import os
import pickle
import tempfile
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import streamlit as st


class Embedder:
    def __init__(self):
        self.PATH = "embeddings"
        self.createEmbeddingsDir()

    def createEmbeddingsDir(self):
        """
        Creates a directory to store the embeddings vectors
        """
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

    def storeDocEmbeds(self, file, original_filename):
        """
        Stores document embeddings using Langchain and FAISS
        """
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            tmp_file.write(file)
            tmp_file_path = tmp_file.name

        def get_file_extension(uploaded_file):
            file_extension = os.path.splitext(uploaded_file)[1].lower()

            return file_extension

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
            length_function=len,
        )

        file_extension = get_file_extension(original_filename)

        if file_extension == ".csv":
            loader = CSVLoader(
                file_path=tmp_file_path,
                encoding="utf-8",
                csv_args={
                    "delimiter": ",",
                },
            )
            data = loader.load()

        elif file_extension == ".pdf":
            loader = PyPDFLoader(file_path=tmp_file_path)
            data = loader.load_and_split(text_splitter)

        elif file_extension == ".txt":
            loader = TextLoader(file_path=tmp_file_path, encoding="utf-8")
            data = loader.load_and_split(text_splitter)

        embeddings = OpenAIEmbeddings(
            openai_api_key=st.session_state["embedding_api_key"]
        )

        vectors = FAISS.from_documents(data, embeddings)
        os.remove(tmp_file_path)

        # Save the vectors to a pickle file
        with open(f"{self.PATH}/{original_filename}.pkl", "wb") as f:
            pickle.dump(vectors, f)

    def getDocEmbeds(self, file=None, original_filename=None):
        """
        Retrieves document embeddings
        """
        if (
            file is not None
            and original_filename is not None
            and not os.path.isfile(f"{self.PATH}/{original_filename}.pkl")
        ):
            self.storeDocEmbeds(file, original_filename)

        return self.merge_all_vectors()

    def merge_all_vectors(self):
        all_vectors = []

        for file in os.listdir(self.PATH):
            if file.endswith("pkl"):
                with open(f"{self.PATH}/{file}", "rb") as f:
                    all_vectors.append(pickle.load(f))

        vectors_merged = None
        if not all_vectors:
            st.warning("请至少上传一个文件", icon="⚠️")
        else:
            vectors_merged = all_vectors[0]
            for i in range(1, len(all_vectors)):
                vectors_merged.merge_from(all_vectors[i])
        return vectors_merged
