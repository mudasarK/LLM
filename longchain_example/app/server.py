from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.chat_models import ChatOllama
from langchain_anthropic import ChatAnthropic
from langserve import add_routes

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

class PromptInput(BaseModel):
    prompt: str

llm = ChatOllama(model="llama3:latest")

@app.post("/llama2/prompt")
async def generate_response(prompt_input: PromptInput):
    response = llm.invoke(prompt_input.prompt)
    return {"response": response}

add_routes(
    app,
    ChatAnthropic(model="llama3:latest"),
    path="/anthropic",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
