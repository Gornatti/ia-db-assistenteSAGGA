#!/usr/bin/env python
"""
CLI Assistant for PostgreSQL Database using AI
"""
import os
import sys
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
console = Console()

class DatabaseAIAssistant:
    def __init__(self, database_url: str, api_key: str):
        self.database_url = database_url
        self.api_key = api_key
        self._initialize_connection()
        self._setup_agent()
    
    def _initialize_connection(self):
        """Inicializa a conexão com o banco de dados"""
        try:
            engine = create_engine(self.database_url)
            self.db = SQLDatabase(engine)
            console.print("✅ Conectado ao banco de dados com sucesso!", style="green bold")
        except Exception as e:
            console.print(f"❌ Erro ao conectar ao banco de dados: {str(e)}", style="red bold")
            sys.exit(1)
    
    def _setup_agent(self):
        """Configura o agente de IA"""
        try:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=self.api_key
            )
            
            toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            self.agent = create_sql_agent(
                llm=self.llm,
                db=self.db,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                verbose=True,
                agent_executor_kwargs={
                    "handle_parsing_errors": True
                }
            )
            console.print("✅ IA configurada com sucesso!", style="green bold")
        except Exception as e:
            console.print(f"❌ Erro ao configurar IA: {str(e)}", style="red bold")
            sys.exit(1)
    
    def run(self):
        """Executa o loop principal do assistente"""
        console.print(Panel.fit(
            "[bold blue]Assistente de Banco de Dados com IA[/bold blue]\n"
            "Digite 'sair' para encerrar\n"
            "Digite 'ajuda' para ver exemplos de perguntas",
            border_style="blue"
        ))
        
        while True:
            try:
                # Recebe pergunta do usuário
                question = Prompt.ask("\n[bold green]Sua pergunta[/bold green]")
                
                if question.lower() in ['sair', 'exit', 'quit']:
                    console.print("\n👋 Até logo!", style="yellow bold")
                    break
                
                if question.lower() in ['ajuda', 'help']:
                    self._show_help()
                    continue
                
                # Processa a pergunta
                with console.status("[bold green]Pensando..."):
                    try:
                        response = self.agent.invoke({"input": question})
                        console.print(Panel(
                            Markdown(response["output"]),
                            title="[bold blue]Resposta",
                            border_style="blue"
                        ))
                    except Exception as e:
                        console.print(f"❌ Erro ao processar pergunta: {str(e)}", style="red bold")
            
            except KeyboardInterrupt:
                console.print("\n\n👋 Encerrando...", style="yellow bold")
                break
            except Exception as e:
                console.print(f"\n❌ Erro inesperado: {str(e)}", style="red bold")
                break
    
    def _show_help(self):
        """Mostra exemplos de perguntas"""
        help_text = """
        **Exemplos de perguntas que você pode fazer:**
        
        - "Mostre todas as tabelas do banco de dados"
        - "Quais são as colunas da tabela usuarios?"
        - "Quantos registros há na tabela clientes?"
        - "Liste os 10 produtos mais vendidos"
        - "Qual foi o total de vendas no último mês?"
        - "Mostre os usuários cadastrados nos últimos 7 dias"
        - "Qual é o valor médio dos pedidos?"
        """
        console.print(Panel(
            Markdown(help_text),
            title="[bold blue]Ajuda",
            border_style="blue"
        ))

def main():
    # Configuração
    DATABASE_URL = "postgresql://postgres.aaoarxvlepzmbainukao:olx5TkpjAZ48snT4@aws-0-eu-west-2.pooler.supabase.com:6543/postgres"
    
    # Solicita a API key do OpenAI
    load_dotenv()
    
    api_key = load_dotenv("OPENAI_API_KEY")
    if not api_key:
        api_key = Prompt.ask("Digite sua OpenAI API Key", password=True)
        if not api_key:
            console.print("❌ API Key é necessária para continuar.", style="red bold")
            sys.exit(1)
    
    # Inicia o assistente
    assistant = DatabaseAIAssistant(DATABASE_URL, api_key)
    assistant.run()

if __name__ == "__main__":
    main()
