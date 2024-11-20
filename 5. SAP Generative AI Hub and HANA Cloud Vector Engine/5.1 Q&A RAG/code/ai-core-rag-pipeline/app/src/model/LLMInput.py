from pydantic import BaseModel

class LLMInput(BaseModel):
    query: str
