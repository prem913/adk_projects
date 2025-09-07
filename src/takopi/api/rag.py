from pydantic import BaseModel
from ..service.rag_service import RAGService
from fastapi import APIRouter

rag_service = RAGService()


router = APIRouter(prefix="/rag")
class RAGRequest(BaseModel):
    documents: list[str]

@router.post("/ingest")
async def ingest_into_rag(request: RAGRequest):
    _ = await rag_service.add_documents(collection_name="frontend_knowledge",documents=request.documents)
    return "done"

class RAGAskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_rag(request: RAGAskRequest):
    return await rag_service.rag_answer(collection_name="frontend_knowledge",question=request.question)




