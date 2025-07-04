from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', 'You are a helpful assistant. Please respond to the user queries.'),
        ('user', 'Question: {question}')
    ]
)

st.title('Langchain OpenSource LLM')
input_text = st.text_input('Search whatever you want')

llm = Ollama(model='llama3.2:latest')  
out_parser = StrOutputParser()
chain = prompt | llm | out_parser

if input_text:
    st.write(chain.invoke({'question': input_text}))
