import streamlit as st
import os


class Sidebar:
    MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4", "baichuan2"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def about():
        about = st.sidebar.expander("🧠 测试 ")
        sections = [
            "#### 测试2",
            "#### 测试1",
        ]
        for section in sections:
            about.write(section)

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

    @staticmethod
    def update_browser_history():
        return ['你的历史文件'] + [
            file.rstrip(".pkl")
            for file in os.listdir("embeddings")
            if file.endswith("pkl")
        ]

    def show_browser_history(self):
        self.current_history = self.update_browser_history()
        with st.sidebar.expander("🗂️ 历史文件", expanded=True):
            return st.selectbox(label="选择文件", options=self.current_history)
