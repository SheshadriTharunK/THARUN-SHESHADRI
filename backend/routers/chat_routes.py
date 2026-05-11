from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatInput(BaseModel):
    message: str

@router.post("/")
async def chat(input: ChatInput):

    # call your LLM here
    response = "Hello from TruthShield GPT"

    return {
        "response": response
    }