import os
import streamlit as st
import psycopg2
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine

# Configuração da página
st.set_page_config(
    page_title="Assistente de Banco de Dados IA",
    page_icon="🤖",
    layout="wide"
)

# CSS customizado
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

# Sidebar com instruções
with st.sidebar:
    st.header("📚 Instruções")
    st.markdown("""
    - Faça perguntas sobre seus dados em linguagem natural
    - A IA criará consultas SQL automaticamente
    - Exemplos de perguntas:
      - "Mostre todas as tabelas"
      - "Quais são os usuários cadastrados?"
      - "Quantos registros há na tabela clientes?"
      - "Qual foi o total de vendas no último mês?"
    """)
    
    st.header("⚙️ Configurações")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("Necessário para o funcionamento da IA")

# Configuração da conexão com o banco de dados
if "db" not in st.session_state:
    DATABASE_URL = "postgresql://postgres.aaoarxvlepzmbainukao:olx5TkpjAZ48snT4@aws-0-eu-west-2.pooler.supabase.com:6543/postgres"
    
    try:
        engine = create_engine(DATABASE_URL)
        db = SQLDatabase(engine)
        st.session_state.db = db
        st.session_state.connection_status = "✅ Conectado ao banco de dados"
    except Exception as e:
        st.session_state.connection_status = f"❌ Erro ao conectar: {str(e)}"

# Exibe status da conexão
st.sidebar.markdown(f"**Status:** {st.session_state.connection_status}")

# Inicializa o histórico de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada do usuário
if prompt := st.chat_input("Faça uma pergunta sobre o banco de dados..."):
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Processa a pergunta e gera resposta
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        if api_key and "db" in st.session_state:
            try:
                # Cria o agente SQL com OpenAI
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0,
                    api_key=api_key
                )
                
                # Cria o agente SQL usando o método atualizado
                agent = create_sql_agent(
                    llm=llm,
                    db=st.session_state.db,
                    agent_type=AgentType.OPENAI_FUNCTIONS,
                    verbose=True,
                    agent_executor_kwargs={
                        "handle_parsing_errors": True
                    }
                )
                
                # Executa a consulta
                with st.spinner("Pensando..."):
                    response = agent.invoke({"input": prompt})
                    response_placeholder.markdown(response["output"])
                
                # Adiciona resposta ao histórico
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

# Botão para limpar histórico
if st.sidebar.button("🧹 Limpar Histórico"):
    st.session_state.messages = []
    st.rerun()

# Informações adicionais no rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Este assistente usa IA para converter perguntas em linguagem natural para consultas SQL.</p>
    <p>Desenvolvido com Streamlit e LangChain 🚀</p>
</div>
""", unsafe_allow_html=True)
