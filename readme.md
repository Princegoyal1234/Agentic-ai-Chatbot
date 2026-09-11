# 🤖 Agentic AI Chatbot

An intelligent **Agentic AI Chatbot** built with modern Generative AI technologies. The chatbot goes beyond simple question-answering by maintaining conversation context, remembering important information about users, querying documents using RAG, and interacting with external tools through a tool/MCP-based architecture.

---

## 🚀 Features

### 💬 1. Simple Chatting

The chatbot can handle normal conversational queries using an LLM.

Example:

```text
User: What is Machine Learning?

AI: Machine Learning is a branch of AI that enables systems
    to learn patterns from data and make predictions...
```

---

### 🕐 2. Conversation History

The chatbot maintains the conversation history so that previous messages can be used to understand the current conversation.

Example:

```text
User: My name is Prince.

AI: Nice to meet you, Prince!

User: What is my name?

AI: Your name is Prince.
```

Conversation history allows the chatbot to maintain context throughout a conversation.

---

### 🧠 3. Short-Term Memory

Short-term memory stores information relevant to the **current conversation/session**.

It allows the chatbot to understand references such as:

```text
User: Explain FastAPI.

AI: FastAPI is a Python framework...

User: Why is it fast?

AI: FastAPI is designed for high-performance...
```

The second question can be understood because the chatbot remembers the current conversation context.

### Purpose

```text
Current Conversation
        ↓
Short-Term Memory
        ↓
Context for LLM
```

---

### 🧠 4. Long-Term Memory

Long-term memory allows the chatbot to retain useful information across conversations.

For example:

```text
Conversation 1:

User: I am learning Python and Generative AI.

                 ↓

Long-Term Memory
                 ↓
"User is learning Python and Generative AI"
```

Later:

```text
New Conversation:

User: What should I learn next?

AI: Since you're working with Python and Generative AI,
you could explore...
```

Long-term memory provides persistent context that can be reused in future conversations.

---

### 📄 5. RAG — Retrieval-Augmented Generation

The chatbot supports **RAG (Retrieval-Augmented Generation)** for querying user-provided documents.

Users can upload documents such as:

```text
PDF
TXT
DOCX
```

The documents are processed and converted into searchable chunks.

The general pipeline is:

```text
              Document
                  ↓
             Text Extraction
                  ↓
               Chunking
                  ↓
             Embeddings
                  ↓
            Vector Database
                  ↓
             User Question
                  ↓
              Retrieval
                  ↓
          Relevant Documents
                  ↓
                 LLM
                  ↓
               Answer
```

Instead of relying only on the LLM's pretrained knowledge, the chatbot retrieves relevant information from the uploaded documents.

Example:

```text
User:
What is the refund policy mentioned in my PDF?

        ↓

RAG Retrieval

        ↓

Relevant PDF chunks

        ↓

LLM

        ↓

Answer based on the document
```

---

### 🛠️ 6. Tool Calling / Tooling

The chatbot can use external tools when answering a question requires an action or external information.

Instead of only generating text:

```text
User
 ↓
LLM
 ↓
Answer
```

the agent can decide:

```text
User
 ↓
LLM
 ↓
Does a tool need to be used?
 ↓
YES
 ↓
Tool
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

This gives the chatbot **agentic capabilities**.

---

### 🔌 7. MCP — Model Context Protocol

The project also incorporates **MCP (Model Context Protocol)** to provide a standardized way for the AI model to interact with external tools and services.

Conceptually:

```text
                    LLM
                     │
                     ↓
                    MCP
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
      Tool 1       Tool 2       Tool 3
        │            │            │
        ↓            ↓            ↓
     Service      Database      API
```

MCP allows tools to be exposed to the AI agent in a structured and reusable manner.

This makes the system easier to extend with new capabilities.

---

# 🧩 Overall Architecture

The chatbot combines multiple AI capabilities into a single system:

```text
                         User
                           │
                           ↓
                    Chatbot Interface
                           │
                           ↓
                    Agent / LLM Layer
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ↓                ↓                 ↓
   Conversation       Short-Term        Long-Term
      History           Memory             Memory
          │                │                 │
          └────────────────┼─────────────────┘
                           │
                           ↓
                    Agent Decision
                           │
              ┌────────────┴────────────┐
              │                         │
              ↓                         ↓
             RAG                    Tool Calling
              │                         │
              ↓                         ↓
       Vector Database                 MCP
                                        │
                              ┌─────────┼─────────┐
                              ↓         ↓         ↓
                            Tool 1    Tool 2    Tool 3
                              │         │         │
                              └─────────┼─────────┘
                                        ↓
                                   Tool Results
                                        │
                                        ↓
                                       LLM
                                        │
                                        ↓
                                  Final Response
                                        │
                                        ↓
                                      User
```

---

# 🏗️ System Components

| Component                | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| **LLM**                  | Generates responses and performs reasoning        |
| **Conversation History** | Maintains previous messages                       |
| **Short-Term Memory**    | Maintains context within the current conversation |
| **Long-Term Memory**     | Stores useful information across conversations    |
| **RAG**                  | Retrieves relevant information from documents     |
| **Vector Database**      | Stores document embeddings for semantic search    |
| **Tools**                | Allow the agent to perform external actions       |
| **MCP**                  | Standardized interface for connecting tools       |
| **FastAPI**              | Backend API layer                                 |
| **Frontend**             | Provides the chatbot user interface               |

---

# 🔄 How a Query Is Processed

When a user sends a message, the system follows an agentic workflow.

```text
User Question
      │
      ↓
Conversation Context
      │
      ↓
Memory Retrieval
      │
      ↓
Agent / LLM
      │
      ├──────────────→ Normal Question
      │                       │
      │                       ↓
      │                  Direct Answer
      │
      ├──────────────→ Document Question
      │                       │
      │                       ↓
      │                      RAG
      │                       │
      │                       ↓
      │                  Retrieved Context
      │                       │
      │                       ↓
      │                      LLM
      │
      └──────────────→ Tool Required
                              │
                              ↓
                             MCP
                              │
                              ↓
                            Tool
                              │
                              ↓
                         Tool Result
                              │
                              ↓
                             LLM
                              │
                              ↓
                        Final Response
```

---

# 🧠 Memory Architecture

The project uses different types of memory for different purposes.

## Short-Term Memory

```text
Current Session
      ↓
Recent Messages
      ↓
Context
      ↓
LLM
```

Used for understanding the current conversation.

## Long-Term Memory

```text
Important User Information
           ↓
      Memory Store
           ↓
      Future Sessions
           ↓
       Memory Retrieval
           ↓
           LLM
```

This allows information to persist beyond a single conversation.

---

# 📚 RAG Architecture

The RAG pipeline consists of two major phases.

## Indexing

```text
PDF
 ↓
Extract Text
 ↓
Split into Chunks
 ↓
Generate Embeddings
 ↓
Store in Vector Database
```

## Retrieval

```text
User Question
 ↓
Generate Query Embedding
 ↓
Similarity Search
 ↓
Retrieve Relevant Chunks
 ↓
Send Context + Question to LLM
 ↓
Generate Answer
```

---

# 🛠️ Tech Stack

The project is built around a modern AI application stack.

```text
Python
FastAPI
LLM
LangChain
RAG
Vector Database
Embeddings
Memory
MCP
Tool Calling
Streamlit / Frontend
```

Depending on the configured environment, individual models, databases, and services can be replaced without changing the overall architecture.

---

# 📁 Project Structure

A possible project structure is:

```text
agentic-ai-chatbot/
│
├── app.py
│
├── api/
│   ├── routes/
│   └── dependencies.py
│
├── agents/
│   ├── agent.py
│   └── prompts.py
│
├── memory/
│   ├── short_term.py
│   └── long_term.py
│
├── rag/
│   ├── document_loader.py
│   ├── chunking.py
│   ├── embeddings.py
│   └── retriever.py
│
├── tools/
│   ├── tools.py
│   └── mcp/
│
├── models/
│   └── schemas.py
│
├── vectorstore/
│
├── frontend/
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

The exact structure may vary depending on the implementation.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <your-repository-url>

cd agentic-ai-chatbot
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
LLM_API_KEY=your_api_key

# Add other required configuration
# VECTOR_DATABASE_URL=...
# DATABASE_URL=...
```

**Never commit `.env` or API keys to GitHub.**

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
```

---

# ▶️ Running the Application

If using FastAPI:

```bash
uvicorn app:app --reload
```

The API will generally be available at:

```text
http://localhost:8000
```

FastAPI's interactive API documentation is available at:

```text
http://localhost:8000/docs
```

---

# 🔌 Example API

### Chat

```http
POST /chat
```

Request:

```json
{
  "message": "Explain machine learning"
}
```

Response:

```json
{
  "answer": "Machine learning is..."
}
```

### Document Query

```http
POST /query
```

Example:

```json
{
  "question": "What is mentioned about the refund policy?"
}
```

---

# 🎯 Project Goals

The primary goal of this project is to build an AI chatbot that behaves more like an **intelligent agent** rather than a simple question-answering application.

The system combines:

- Natural language conversation
- Context awareness
- Short-term memory
- Long-term memory
- Document understanding
- RAG
- Tool calling
- MCP
- API-based architecture

This enables the chatbot to **understand, remember, retrieve information, use tools, and generate contextual responses**.

---

# 🔮 Future Improvements

Potential future enhancements include:

- Multi-agent architecture
- More external tools
- Better memory management
- Streaming LLM responses
- Authentication and authorization
- User-specific document collections
- Conversation management
- Advanced agent planning
- Observability and tracing
- Evaluation framework
- Production deployment with Docker
- Cloud deployment
- More MCP servers and tools

---

# 👨‍💻 Author

**Prince Goyal**

This project demonstrates the development of a modern **Agentic AI application** combining LLMs, RAG, memory, tool calling, MCP, and API-based backend architecture.
