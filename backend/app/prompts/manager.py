import os
from typing import Dict, Optional

from app.core.config import settings
from app.core.logger import logger
from langfuse import Langfuse

# Fallback local prompt definitions for quick iteration
DEFAULT_PROMPTS: Dict[str, str] = {
    "contextualize_q_system": (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    ),
    "qa_system": (
        "You are given a user question, and please write clean, concise and accurate answer to the question. "
        "You will be given a set of related contexts to the question, which are numbered sequentially starting from 1. "
        "Each context has an implicit reference number based on its position in the array (first context is 1, second is 2, etc.). "
        "Please use these contexts and cite them using the format [citation:x] at the end of each sentence where applicable. "
        "Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. "
        "Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. "
        "Say 'information is missing on' followed by the related topic, if the given context do not provide sufficient information. "
        "If a sentence draws from multiple contexts, please list all applicable citations, like [citation:1][citation:2]. "
        "Other than code and specific names and citations, your answer must be written in the same language as the question. "
        "Be concise.\n\nContext: {context}\n\n"
        "Remember: Cite contexts by their position number (1 for first context, 2 for second, etc.) and don't blindly "
        "repeat the contexts verbatim."
    ),
    "document_prompt": ("\n\n- {page_content}\n\n"),
}


class PromptManager:
    def __init__(self):
        self.use_langfuse = bool(
            settings.LANGFUSE_HOST
            and settings.LANGFUSE_PUBLIC_KEY
            and settings.LANGFUSE_SECRET_KEY
        )
        self.prompts = DEFAULT_PROMPTS

        if self.use_langfuse:
            try:
                self._lf_client = Langfuse(
                    host=settings.LANGFUSE_HOST,
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                )
            except Exception as e:
                logger.error(f"Error loading prompts from Langfuse: {e}")
                self._lf_client = None
                self.use_langfuse = False

    def get_prompt(self, name: str, variables: Optional[dict] = None) -> str:
        if self.use_langfuse and self._lf_client:
            try:
                prompt_key = f"llmops/{name}"
                prompt = self._lf_client.get_prompt(prompt_key)
                if variables:
                    compiled_prompt = prompt.compile(**variables)
                    return compiled_prompt
                return prompt.compile()
            except Exception as e:
                logger.error(f"Error getting prompt from Langfuse: {e}")
                pass

        tmpl = self.prompts.get(name)
        if tmpl is None:
            raise KeyError(f"Prompt {name} not found")
        if variables:
            return tmpl.format(**variables)
        return tmpl

    def set_prompt(self, prompt_name: str, prompt: str):
        self.prompts[prompt_name] = prompt


prompt_manager = PromptManager()
