from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .chat import router as chat_router
from .files import router as files_router
from .threads import router as thread_router
app = FastAPI(
    title="LangGraph RAG Chatbot API",
    version="1.0.0",
)
app.include_router(
    chat_router
)
app.include_router(files_router)

app.include_router(thread_router)

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():

    return {
        "message": "LangGraph RAG API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    } 