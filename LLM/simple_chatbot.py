# #0.2  https://python.langchain.com/v0.2/docs/tutorials/chatbot/


import logging
from fastapi import FastAPI , Request, Response, Depends, Cookie
from itsdangerous import URLSafeTimedSerializer, BadSignature
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
#from langchain_community.chat_models import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory
from langserve import add_routes
import getpass
from langchain_anthropic import ChatAnthropic
import os
import uuid


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#model = ChatOllama(model="llama3:latest")

# Set API key from environment variable or use getpass for security
if "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = getpass.getpass("Enter Anthropic API Key: ")
model = ChatAnthropic(model="claude-3-sonnet-20240229")

class ChatMessageHistory:
    def __init__(self):
        self.messages = []

    def append(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
    MessagesPlaceholder(variable_name="messages"),
])

chain = prompt | model
with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
#config = {"configurable": {"session_id": "abc2"}}

app = FastAPI(
    title="Fast API Chat assistant",
    version="1.0",
    description="A simple API server using LLM and FastAPI Runnable interfaces",
)

# Add session middleware
#app.add_middleware(SessionMiddleware, secret_key="session_manager_key_123_&&*")
# Serializer for session cookie
secret_key = "session_manager_key_123_&&*"
serializer = URLSafeTimedSerializer(secret_key)


add_routes(app, chain, path="/chain")

chat_history = []

class MessageRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/send_message")
async def send_message(request: Request, response: Response, message: MessageRequest, session_id: str = Cookie(None)):
    user_message = message.message

    # If session_id is not present or invalid, create a new session
    if session_id is None:
        session_id = str(uuid.uuid4())
        session_cookie = serializer.dumps(session_id)
        response.set_cookie(key="session_id", value=session_cookie)
    else:
        try:
            session_id = serializer.loads(session_id, max_age=3600)  # session valid for 1 hour
        except BadSignature:
            session_id = str(uuid.uuid4())
            session_cookie = serializer.dumps(session_id)
            response.set_cookie(key="session_id", value=session_cookie)

    logger.debug(f"Received message: {user_message} for session: {session_id}")

    chat_history = get_session_history(session_id)
    chat_history.append({"role": "human", "content": user_message})
    logger.debug(f"Updated chat history for session {session_id}: {chat_history.get_messages()}")

    try:
        response_data = with_message_history.invoke(
            {
                "messages": chat_history.get_messages(),
                "language": "English",
            },
            config={"configurable": {"session_id": session_id}},
        )
        ai_response = response_data.content
        chat_history.append({"role": "ai", "content": ai_response})
        logger.debug(f"AI response for session {session_id}: {ai_response}")

        return {"response": ai_response}
    except Exception as e:
        logger.error(f"Error invoking with_message_history for session {session_id}: {e}")
        return {"error": str(e)}


'''
#0.2  https://python.langchain.com/v0.2/docs/tutorials/chatbot/

#!/usr/bin/env python
from typing import List

from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
#from langchain_openai import ChatOpenAI
from langserve import add_routes
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. Create model
model  =  ChatOllama(model="llama3:latest") #// ChatOpenAI()

#2 chat history store
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

#3 create a template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | model


with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages",
)

config = {"configurable": {"session_id": "abc2"}}



# 3. Create parser
# parser = StrOutputParser()

# # 4. Create chain
# chain = prompt_template | model | parser


# 4. App definition
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

# 5. Adding chain route

add_routes(
    app,
    chain,
    path="/chain",
)

# Store chat history in a simple in-memory structure for this example
# Store chat history in a simple in-memory structure for this example
chat_history = []

class MessageRequest(BaseModel):
    message: str

@app.post("/send_message")
async def send_message(request: MessageRequest):
    user_message = request.message

    # Append new user message to chat history
    chat_history.append({"role": "human", "content": user_message})

    # Invoke LangServe with the updated chat history
    response = with_message_history.invoke(
        {
            "messages": chat_history,
            "language": "English",
        },
        config=config,
    )

    # Append AI response to chat history
    ai_response = response.content
    chat_history.append({"role": "ai", "content": ai_response})

    # Return the AI response to the frontend
    return {"response": ai_response}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

'''
