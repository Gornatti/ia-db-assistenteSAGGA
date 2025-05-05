# IA Assistente com GPT-3.5-Turbo

import os
import streamlit as st
import psycopg2
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine

st.set_page_config(page_title="Assistente de Banco de Dados IA", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stChat {
        max-width: 1000px;
        margin: 0 auto;
    }
    .stTextInput > div > div > input {
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Assistente de Banco de Dados com IA")
st.markdown("Converse com seu banco de dados PostgreSQL de forma natural!")

with st.sidebar:
    st.header("📚 Instruções")
    st.markdown("""
    - Faça perguntas sobre seus dados em linguagem natural
    - A IA criará consultas SQL automaticamente
    """)
    
    st.header("⚙️ Configurações")
    api_key = st.text_input("OpenAI API Key", type="password")

if "db" not in st.session_state:
    DATABASE_URL = os.getenv("DATABASE_URL")
    try:
        engine = create_engine(DATABASE_URL)
        db = SQLDatabase(engine)
        st.session_state.db = db
        st.session_state.connection_status = "✅ Conectado ao banco de dados"
    except Exception as e:
        st.session_state.connection_status = f"❌ Erro ao conectar: {str(e)}"

st.sidebar.markdown(f"**Status:** {st.session_state.connection_status}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Faça uma pergunta sobre o banco de dados..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        if api_key and "db" in st.session_state:
            try:
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0,
                    api_key=api_key
                )
                
                agent = create_sql_agent(
                    llm=llm,
                    db=st.session_state.db,
                    agent_type=AgentType.OPENAI_FUNCTIONS,
                    verbose=True,
                    agent_executor_kwargs={"handle_parsing_errors": True}
                )
                
                with st.spinner("Pensando..."):
                    response = agent.invoke({"input": prompt})
                    response_placeholder.markdown(response["output"])
                
                st.session_state.messages.append({"role": "assistant", "content": response["output"]})
                
            except Exception as e:
                error_msg = f"Erro ao processar sua pergunta: {str(e)}"
                response_placeholder.markdown(f"❌ {error_msg}")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        elif not api_key:
            error_msg = "Por favor, insira sua OpenAI API Key na barra lateral."
            response_placeholder.markdown(f"❌ {error_msg}")
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        else:
            error_msg = "Erro de conexão com o banco de dados."
            response_placeholder.markdown(f"❌ {error_msg}")
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

if st.sidebar.button("🧹 Limpar Histórico"):
    st.session_state.messages = []
    st.rerun()
