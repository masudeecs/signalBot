from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import OpenAIEmbeddings


from config.security import get_llm
llm = get_llm()
# 
async def question_and_answer(ques: str, session_name):
    
    vectorstore = Chroma(persist_directory="./all_data", embedding_function=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()


    ### Contextualize question ###
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )


    ### Answer question ###
    # qa_system_prompt = """You are an Artificial Intelligence Tutor of Signal ans System subject. \
    # You task is to help student to understand Signal ans System subject concept \
    # and help them to solve problem step by step. You should not solve the problem directly, \
    # rather you help them to learn and solve the problem step by step. \
    # Use the following pieces of retrieved context to answer the question. \
    # If you don't know the answer, just say that you don't know. \
    # Use three sentences maximum and keep the answer concise.\

    # {context}"""

    qa_system_prompt = """ You are a Artificial Intelligence Tutor of Signal ans System subject. \
            You task is to help student to understand Signal ans System subject concept \
            and help them to solve problem step by step. You should not solve the problem directly, \
            rather you help them to learn and solve the problem gradually and also make sure that \
            your response are in latex. If you cannot find the answer from the pieces of context, \
            just say that you don't know, don't try to make up an answer. \
            
            {context} """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


    ### Statefully manage chat history ###
    store = {}


    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]


    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    response = conversational_rag_chain.invoke(
        {"input": ques},
        config={"configurable": {"session_id": session_name}},
    )["answer"]

    return response