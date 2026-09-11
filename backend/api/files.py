from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from ..rag import create_vectorstore


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post("/upload")
async def upload_pdf(
    thread_id: str = Form(...),
    file: UploadFile = File(...),
):

    try:

        # Check file type
        if file.content_type != "application/pdf":

            return JSONResponse(
                status_code=400,
                content={
                    "error": "Only PDF files are allowed."
                },
            )


        file_bytes = await file.read()
        result=create_vectorstore(
            file_bytes=file_bytes,
            thread_id=thread_id,
            filename=file.filename,
        )


        return result


    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )