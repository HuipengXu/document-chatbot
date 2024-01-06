import os
import streamlit as st
from streamlit_chat import message


class ChatHistory:
    def __init__(self):
        self.history = st.session_state.get("history", [])
        st.session_state["history"] = self.history

    def initialize(self):
        if "assistant" not in st.session_state:
            st.session_state["assistant"] = ["你好 ! 🤗"]
        if "user" not in st.session_state:
            st.session_state["user"] = []

    def reset(self):
        st.session_state["history"] = []

        self.initialize()
        st.session_state["reset_chat"] = False

    def append(self, mode, message):
        st.session_state[mode].append(message)

    def generate_messages(self, container):
        if st.session_state["assistant"]:
            with container:
                message(
                    st.session_state["assistant"][0],
                    key=str(0),
                    avatar_style="thumbs",
                )
                for i in range(1, len(st.session_state["assistant"])):
                    message(
                        st.session_state["user"][i - 1],
                        is_user=True,
                        key=f"history_{i-1}_user",
                        avatar_style="big-smile",
                    )
                    message(
                        st.session_state["assistant"][i],
                        key=str(i),
                        avatar_style="thumbs",
                    )

    def load(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = f.read().splitlines()

    def save(self):
        with open(self.history_file, "w") as f:
            f.write("\n".join(self.history))
