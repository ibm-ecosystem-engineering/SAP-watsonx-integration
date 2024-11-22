from pydantic import BaseModel

class LLMOutput(BaseModel):
    response: str