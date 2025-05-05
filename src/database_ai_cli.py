import os
import sys
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

console = Console()

def connect_db():
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        return SQLDatabase(engine)
    except Exception as e:
        console.print(f"❌ Erro ao conectar ao banco de dados: {e}", style="red bold")
        sys.exit(1)

def get_llm(api_key):
    try:
        return ChatOpenAI(model="gpt-4-turbo", api_key=api_key, temperature=0)
    except:
        return ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, temperature=0)

def main():
    load_dotenv()
    db = connect_db()
    api_key = os.getenv("OPENAI_API_KEY") or Prompt.ask("Digite sua OpenAI API Key", password=True)
    if not api_key:
        console.print("❌ API Key obrigatória.", style="red bold")
        sys.exit(1)

    llm = get_llm(api_key)
    agent = create_sql_agent(llm=llm, db=db, agent_type=AgentType.OPENAI_FUNCTIONS, verbose=True)

    console.print(Panel.fit(
        "[bold blue]Assistente de Banco de Dados com IA[/bold blue]\n"
        "Digite 'sair' para encerrar",
        border_style="blue"
    ))

    while True:
        try:
            question = Prompt.ask("\n[bold green]Sua pergunta[/bold green]")
            if question.lower() in ["sair", "exit", "quit"]:
                console.print("\n👋 Encerrando...", style="yellow bold")
                break

            with console.status("[bold green]Pensando..."):
                try:
                    response = agent.invoke({"input": question})
                    console.print(Panel(
                        Markdown(response["output"]),
                        title="[bold blue]Resposta",
                        border_style="blue"
                    ))
                except Exception as e:
                    console.print(f"❌ Erro ao processar pergunta: {e}", style="red bold")

        except KeyboardInterrupt:
            console.print("\n\n👋 Encerrando...", style="yellow bold")
            break
        except Exception as e:
            console.print(f"❌ Erro inesperado: {e}", style="red bold")
            break

if __name__ == "__main__":
    main()

