import base64
import json
import traceback

from app.core.config import settings
from app.core.logger import logger
from app.crud.document import get_documents_by_knowledge_base_id
from app.crud.knowledge import get_knowledge_base_by_ids
from app.models.chat import Message
from app.prompts.manager import prompt_manager
from app.services.embeddings.embedding_factory import EmbeddingFactory
from app.services.langfuse_tracing import langfuse_handler
from app.services.llm.factory import LLMFactory
from app.services.vector_store.factory import VectorStoreFactory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_response(
    user_id: int,
    query: str,
    messages: dict,
    knowledge_base_ids: list[int],
    chat_id: int,
    db: AsyncSession,
    rails_service: RunnableRails,
):
    try:
        # create user message
        user_message = Message(
            role="user",
            content=query,
            chat_id=chat_id,
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        # create bot message placeholder
        bot_message = Message(
            role="assistant",
            content="",
            chat_id=chat_id,
        )
        db.add(bot_message)
        await db.commit()
        await db.refresh(bot_message)

        # get knowledge bases and their documents
        knowledge_bases = await get_knowledge_base_by_ids(db, knowledge_base_ids)

        # initialize embeddings
        embeddings = EmbeddingFactory.create()

        vector_stores = []
        for kb in knowledge_bases:
            documents = await get_documents_by_knowledge_base_id(db, kb.id)
            if documents:
                vector_store = VectorStoreFactory.create(
                    store_type=settings.VECTOR_STORE_PROVIDER,
                    collection_name=f"knowledge_base_{kb.id}",
                    embedding_function=embeddings,
                )
                vector_stores.append(vector_store)
                # logger.info(
                #     f"Collection {kb.id} loaded: {vector_store._store._collection.count()} documents"
                # )
        if not vector_stores:
            error_message = "No documents found for the provided knowledge bases"
            yield error_message
            bot_message.content = error_message
            await db.commit()
            return

        # TODO: Use multiple retrievers
        retriever = vector_stores[0].as_retriever()

        # initialize LLM model
        llm = LLMFactory.create()

        # Create contextualize question prompt
        contextualize_q_system_prompt = prompt_manager.get_prompt(
            "contextualize_q_system"
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # Create history aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # Create QA prompt
        qa_system_prompt = prompt_manager.get_prompt("qa_system")
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # Create Document stuff chain
        document_prompt = PromptTemplate.from_template(
            prompt_manager.get_prompt("document_prompt")
        )
        question_answer_chain = create_stuff_documents_chain(
            llm,
            qa_prompt,
            document_variable_name="context",
            document_prompt=document_prompt,
        )

        # Create retrieval chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )
        rag_chain_with_rails = rails_service | rag_chain

        # Generate response
        chat_history = []
        for message in messages["messages"]:
            if message["role"] == "user":
                chat_history.append({"type": "human", "content": message["content"]})
            elif message["role"] == "assistant":
                message["content"] = message["content"].split("__LLM_RESPONSE__")[-1]
                chat_history.append({"type": "ai", "content": message["content"]})

        response = ""
        async for chunk in rag_chain_with_rails.astream(
            {"input": query, "chat_history": chat_history},
            config={
                "callbacks": [langfuse_handler],
                "metadata": {"langfuse_user_id": user_id},
            },
        ):
            if "context" in chunk:
                serializable_context = []
                for context in chunk["context"]:
                    serializable_context.append(
                        {
                            "page_content": context.page_content.replace('"', '\\"'),
                            "metadata": context.metadata,
                        }
                    )
                escaped_context = json.dumps({"context": serializable_context})
                base64_context = base64.b64encode(escaped_context.encode()).decode()
                separator = "__LLM_RESPONSE__"
                yield f'0:"{base64_context}{separator}"\n'
                response += base64_context + separator

            if "answer" in chunk and chunk["answer"] is not None:
                response += chunk["answer"]
                escape_chunk = chunk["answer"].replace('"', '\\"').replace("\n", "\\n")
                yield f'0:"{escape_chunk}"\n'
        bot_message.content = response
        await db.commit()
    except Exception as e:
        traceback.print_exc()
        error_message = f"Error generating response: {str(e)}"
        logger.error(error_message)
        yield f"3:{error_message}\n"
        bot_message.content = error_message
        await db.commit()
