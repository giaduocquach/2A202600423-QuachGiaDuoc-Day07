from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved_chunks = self.store.search(question, top_k=top_k)

        if not retrieved_chunks:
            prompt = (
                "You are a helpful assistant.\n"
                "No supporting context was retrieved from the knowledge base.\n"
                f"Question: {question}\n"
                "Answer honestly and note uncertainty if needed."
            )
            return str(self.llm_fn(prompt))

        context_blocks = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            context_blocks.append(f"[{index}] {chunk['content']}")
        context_text = "\n\n".join(context_blocks)

        prompt = (
            "You are a helpful assistant. Use only the provided context to answer the question.\n"
            "If the context is insufficient, say what is missing.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return str(self.llm_fn(prompt))
