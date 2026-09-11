import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from .config import (
    UPLOAD_DIR,
    VECTORSTORE_DIR,
)


# =====================================================
# EMBEDDINGS
# =====================================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# =====================================================
# VECTORSTORE CACHE
# =====================================================

VECTORSTORE_CACHE = {}


# =====================================================
# CREATE VECTORSTORE
# =====================================================

def create_vectorstore(
    file_bytes,
    thread_id,
    filename
):
    thread_upload_dir=(UPLOAD_DIR/thread_id)
    os.makedirs(
        thread_upload_dir,
        exist_ok=True,
    )

    pdf_path = (
        thread_upload_dir /
        f"{filename}.pdf"
    )

    with open(
        pdf_path,
        "wb",
    ) as f:

        f.write(
            file_bytes
        )

    loader = PyPDFLoader(
        str(pdf_path)
    )

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(
        docs
    )

    vectorstore_path=VECTORSTORE_DIR/thread_id
    vectorstore_path.mkdir(
        parents=True,
        exist_ok=True,
    )
    faiss_file = (
        vectorstore_path /
        "index.faiss"
    )
    pkl_file = (
        vectorstore_path /
        "index.pkl"
    )
    if (
        not faiss_file.exists()
        or
        not pkl_file.exists()
    ):

        vectorstore = FAISS.from_documents(
            chunks,
            embeddings,
        )
    
    else:
        # ---------------------------------------------
        # Load existing vectorstore
        # ---------------------------------------------

        vectorstore = FAISS.load_local(
            vectorstore_path,
            embeddings,
            allow_dangerous_deserialization=True,
        )

        # ---------------------------------------------
        # Add new PDF chunks
        # ---------------------------------------------

        vectorstore.add_documents(
            chunks
        )


    # -------------------------------------------------
    # Save updated vectorstore
    # -------------------------------------------------

    vectorstore.save_local(
        vectorstore_path
    )

    VECTORSTORE_CACHE[
        thread_id
    ] = vectorstore
    return {
        "success": True,
        "filename": filename,
        "thread_id": thread_id,
        "chunks": len(chunks),
    }



# =====================================================
# PDF SEARCH
# =====================================================

def search_pdf(
    query,
    thread_id,
):

    vectorstore_path = (
        VECTORSTORE_DIR /
        f"{thread_id}"
    )

    if not vectorstore_path.exists():
        return {
            "error":
                "No PDF uploaded for this chat."
        }

    if thread_id not in VECTORSTORE_CACHE:

        VECTORSTORE_CACHE[
            thread_id
        ] = FAISS.load_local(
            vectorstore_path,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    retriever = (
        VECTORSTORE_CACHE[
            thread_id
        ].as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 4
            },
        )
    )

    docs = retriever.invoke(
        query
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    metadata = [
        doc.metadata
        for doc in docs
    ]

    return {
        "context": context,
        "metadata": metadata,
    }