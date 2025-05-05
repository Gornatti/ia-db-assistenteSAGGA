# IA DB Assistente SAGGA 🤖

Assistente com IA para interagir com bancos de dados PostgreSQL usando linguagem natural e GPT-4.

## Funcionalidades

- Consulta ao banco por texto natural (PT-BR)
- Interface web com Streamlit
- Interface em linha de comando (CLI)
- Tradução automática das perguntas para SQL via OpenAI

## Como usar

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Criar um `.env` com:

```
DATABASE_URL=postgresql://<sua-url>
OPENAI_API_KEY=sk-<sua-chave>
```

### 3. Rodar interface Web (Streamlit)

```bash
streamlit run src/database_ai_assistant.py
```

### 4. Rodar interface CLI

```bash
python src/database_ai_cli.py
```

---

Desenvolvido como parte do projeto SAGGA ⚙️🧠
