import streamlit as st

# from langchain.chat_models import ChatBaichuan
from .baichuan import ChatBaichuan
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback

# fix Error: module 'langchain' has no attribute 'verbose'
import langchain

langchain.verbose = False


class Chatbot:
    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    qa_template = """
        您现在是一个有帮助的AI助手。用户提供给您一个文件，其内容由以下上下文片段表示，请使用它们来回答最后的问题。
        如果您不知道答案，请坦率地说您不知道。请不要试图编造答案。
        如果问题与上下文无关，请礼貌地回答您只回答与上下文相关的问题。
        在回答时尽量提供尽可能多的细节。必须使用中文回答

        context: {context}
        =========
        question: {question}
        ======
        """

    QA_PROMPT = PromptTemplate(
        template=qa_template, input_variables=["context", "question"]
    )

    def conversational_chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        llm = ChatBaichuan(
            temperature=self.temperature,
            baichuan_api_key=st.session_state["chat_api_key"],
        )

        retriever = self.vectors.as_retriever()

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            verbose=True,
            return_source_documents=True,
            max_tokens_limit=4097,
            combine_docs_chain_kwargs={"prompt": self.QA_PROMPT},
        )

        chain_input = {"question": query, "chat_history": st.session_state["history"]}
        result = chain(chain_input)

        st.session_state["history"].append((query, result["answer"]))
        # count_tokens_chain(chain, chain_input)
        return result["answer"]


def count_tokens_chain(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        st.write(f"###### Tokens used in this conversation : {cb.total_tokens} tokens")
    return result
