import streamlit as st
import pandas as pd
import os


class Sidebar:
    MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4", "baichuan2"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def reset_chat_button():
        if st.button("重置对话"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature

    def show_options(self):
        with st.sidebar.expander("🛠️ 设 置", expanded=True):
            self.reset_chat_button()
            self.model_selector()
            self.temperature_slider()
            st.session_state.setdefault("模型", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("温度", self.TEMPERATURE_DEFAULT_VALUE)

    def show_file_list(self):
        current_history = [
            file.rstrip(".pkl")
            for file in os.listdir("embeddings")
            if file.endswith("pkl")
        ]
        with st.sidebar.expander("🗂️ 历史文件", expanded=False):
            df = pd.DataFrame(current_history, columns=["文件列表"])
            st.table(df)
