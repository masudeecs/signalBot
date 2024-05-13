from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from openai import AsyncStream
from openai.types.chat import ChatCompletionChunk

from fastapi.responses import JSONResponse

from config.security import get_llm, get_settings, get_audio_openai

settings = get_settings()

client = get_audio_openai()

chat_history_for_chain = ChatMessageHistory()

# async def content_generator(ques):
#     # ChatOpenAI
#     llm = get_llm()
#     response = llm.invoke(ques.prompt)
#     return JSONResponse(content=response.content)

async def question_and_answer(ques: str, session_name):
    chat = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """As an LLM model, you are a mental health bot. 
                Your responses should be focused exclusively on mental health-related questions. 
                If you encounter a query that isn't related to mental health, please reply with I don't know.""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | chat | StrOutputParser()
    chain_with_message_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: chat_history_for_chain,
        # lambda session_id: SQLChatMessageHistory(
        #     session_id=session_id, connection_string=settings.SQLALCHEMY_CHAT_DATABASE_URL
        # ),
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    response = chain_with_message_history.invoke(
            {"input": ques},
            {"configurable": {"session_id": session_name}},
        )
    # print(response)
    # print(JSONResponse(content=response))
    return response 
    # return JSONResponse(content=response)
    # return JSONResponse(content=response.content)

async def text_to_speech_stream_openai(text: str):
    print('Generating audio from text review using Open AI API')
    #without stream=True is: response: HttpxBinaryResponseContent
    stream: AsyncStream[ChatCompletionChunk] = await client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=text,
        # stream=True
    ) #type: ignore
    #print(type(response), dir(response), response)
    print(type(stream), dir(stream), stream)
    return stream