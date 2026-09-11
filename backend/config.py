import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"

VECTORSTORE_DIR = BASE_DIR / "vectorstores"

DB_PATH = BASE_DIR / "chatbot.db"


UPLOAD_DIR.mkdir(
  parents=True,
    exist_ok=True
)

VECTORSTORE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


POSTGRES_URI = os.getenv(
    "POSTGRES_URI",
    "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
)




os.environ["LANGCHAIN_PROJECT"] = " LangGraph RAG Chatbot"