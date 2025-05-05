import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine

st.set_page_config(page_title="Assistente de Banco de Dados IA", page_icon="🤖", layout="wide")

st.title("🤖 SAGGA")
st.caption("Natural Language Data Relationship")

with st.sidebar:
    st.header("📚 Instruções")
    st.markdown("""
    - Faça perguntas sobre seus dados em linguagem natural
    - SAGGA em fase de testes
    - Feito por Antonio Gornatti
    """)
    st.header("⚙️ Configurações")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("Status: ✅ Conectado ao banco de dados" if "db" in st.session_state else "Status: ❌ Não conectado")

# Inicializar banco
if "db" not in st.session_state:
    DATABASE_URL = os.getenv("DATABASE_URL")
    try:
        engine = create_engine(DATABASE_URL)
        st.session_state.db = SQLDatabase(engine)
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Faça uma pergunta sobre o banco de dados..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        if not api_key:
            msg = "❌ Por favor, insira sua OpenAI API Key na barra lateral."
            placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
        else:
            try:
                try:
                    llm = ChatOpenAI(model="gpt-4-turbo", api_key=api_key, temperature=0)
                except:
                    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, temperature=0)

                agent = create_sql_agent(
                    llm=llm,
                    db=st.session_state.db,
                    agent_type=AgentType.OPENAI_FUNCTIONS,
                    verbose=True,
                    agent_executor_kwargs={"handle_parsing_errors": True}
                )
                with st.spinner("Pensando..."):
                    result = agent.invoke({"input": prompt})
                    placeholder.markdown(result["output"])
                    st.session_state.messages.append({"role": "assistant", "content": result["output"]})
            except Exception as e:
                error_msg = f"❌ Erro ao processar sua pergunta: {str(e)}"
                placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

if st.sidebar.button("🧹 Limpar Histórico"):
    st.session_state.messages = []
    st.rerun()
