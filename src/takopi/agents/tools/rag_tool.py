from takopi.service.rag_service import RAGService


class RAGTool():
    def __init__(self,rag_service) -> None:
        self.rag_service = rag_service

    async def knowledge_sensei(self,query: str) -> str:
        """
        knowledge_sensei retrievs knowledge from a knowledge base based on query
        """

        knowledge = await self.rag_service.rag_answer("frontend_knowledge",query)
        return knowledge
