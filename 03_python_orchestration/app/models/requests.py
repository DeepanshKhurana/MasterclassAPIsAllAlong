from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: str = Field(description="Message author: 'user' or 'assistant'")
    content: str = Field(description="Text content of the message")


class ChatRequest(BaseModel):
    message: str = Field(description="The user's chat message")
    history: list[ChatTurn] | None = Field(
        default=None,
        description="Prior conversation turns, oldest first",
    )
