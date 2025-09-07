import chromadb
import uuid
from chromadb.api.models.CollectionCommon import np
from google.genai.types import EmbedContentConfig
from chromadb.config import Settings

from takopi.dependency import get_gemini_model

from common.core.logging import logging

logger = logging.getLogger(__name__)

class RAGService:
    """
    A service class to interact with ChromaDB, using Google's Generative AI
    for embedding generation and Retrieval-Augmented Generation (RAG).
    """

    def __init__(self, host="localhost", port=8888):
        """
        Initializes the service, connects to ChromaDB, and sets up the AI models.

        Args:
            host (str): The hostname of the ChromaDB server.
            port (int): The port of the ChromaDB server.
        """
        try:
            # 1. Initialize ChromaDB Client
            # This client connects to a running ChromaDB instance.
            self.client = chromadb.HttpClient(host=host, port=port,settings=Settings(anonymized_telemetry=False))
            # Ping the server to ensure a connection is established.
            self.client.heartbeat()
            self.gemini_model = get_gemini_model()

        except Exception as e:
            logger.error(f"Error intializing rag service : {e}")
            raise

    def get_or_create_collection(self, collection_name: str):
        """
        Retrieves a collection from ChromaDB or creates it if it doesn't exist.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            chromadb.Collection: The collection object.
        """
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            logging.info(f"Collection '{collection_name}' ready.")
            return collection
        except Exception as e:
            logging.error(f"Error getting or creating collection '{collection_name}': {e}")
            raise

    async def add_documents(self, collection_name: str, documents: list[str]):
        """
        Adds a list of text documents to a specified collection.
        It generates embeddings for each document before adding.

        Args:
            collection_name (str): The name of the collection.
            documents (list[str]): A list of strings, where each string is a document.
        """
        if not documents:
            logger.info("No documents to add.")
            return

        collection = self.get_or_create_collection(collection_name)

        logger.info(f"Generating embeddings for {len(documents)} documents...")
        try:
            # Generate embeddings for the documents using the Google AI model
            embed_config = EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            response = await self.gemini_model.embed_content(
                model="models/embedding-001",
                contents=documents,
                config=embed_config
            )
            embeddings = response.embeddings

            # Generate unique IDs for each document
            ids = [str(uuid.uuid4()) for _ in documents]

            logger.info("Adding documents to the collection...")
            # Add the documents, their embeddings, and unique IDs to the collection
            if embeddings:
                embedding_np = np.array([embedding.values for embedding in embeddings])
                logger.info(embedding_np.tolist())
                collection.add(
                    ids=ids,
                    embeddings=embedding_np,
                    documents=documents
                )
            logger.info(f"Successfully added {len(documents)} documents to '{collection_name}'.")

        except Exception as e:
            logger.info(f"Failed to add documents: {e}")
            raise

    async def query(self, collection_name: str, query_text: str, n_results: int = 50):
        """
        Queries a collection to find the most similar documents to a given text.

        Args:
            collection_name (str): The name of the collection to query.
            query_text (str): The text to search for.
            n_results (int): The number of similar documents to return.

        Returns:
            dict: A dictionary containing the query results, or None on failure.
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            # Generate an embedding for the query text
            embed_config = EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            response = await self.gemini_model.embed_content(
                model="models/embedding-001",
                contents=[query_text],
                config=embed_config
            )
            query_embedding = response.embeddings

            # Perform the query on the collection
            if query_embedding:
                embeddings = np.array([embedding.values for embedding in query_embedding])
                logger.info(embeddings.tolist())
                results = collection.query(
                    query_embeddings=embeddings,
                    n_results=n_results
                )
                return results
        except Exception as e:
            logger.error(f"Error during query: {e}")
            return None

    async def rag_answer(self, collection_name: str, question: str, n_results: int = 50):
        """
        Performs Retrieval-Augmented Generation (RAG).
        1. Retrieves relevant documents from ChromaDB based on the question.
        2. Feeds these documents as context to a generative model to get an answer.

        Args:
            collection_name (str): The collection containing the knowledge base.
            question (str): The user's question.
            n_results (int): The number of documents to retrieve for context.

        Returns:
            str: The generated answer.
        """
        logger.info(f"\n--- Starting RAG for question: '{question}' ---")
        # 1. Retrieval
        logger.info("Step 1: Retrieving relevant documents...")
        retrieved_results = await self.query(collection_name, question, n_results)
        logger.info(str(retrieved_results))

        # Combine the retrieved documents into a single context string.
        context = ""
        if retrieved_results and retrieved_results['documents']:
            context = "\n".join(retrieved_results['documents'][0])
            logger.info(f"Step 2: Found context:\n---\n{context}\n---")
        return context

        # # 2. Generation
        # # Create a prompt that instructs the model on how to behave.
        # prompt = f"""
        # Based ONLY on the following context, please provide a clear and concise answer to the question.
        # If the context does not contain the answer, state that you don't have enough information.
        #
        # CONTEXT:
        # {context}
        #
        # QUESTION:
        # {question}
        #
        # ANSWER:
        # """

        # logger.info("Step 3: Generating answer with Gemini...")
        # try:
        #     response = await self.gemini_model.generate_content(model="gemini-2.0-flash",contents=prompt)
        #     return response.text
        # except Exception as e:
        #     logger.error(f"Error during answer generation: {e}")
        #     return "There was an error while generating the answer."
