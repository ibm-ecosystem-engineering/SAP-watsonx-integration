# Get embeddings
from dotenv import load_dotenv
load_dotenv()
from gen_ai_hub.proxy.native.openai import embeddings


class Embedding:
    def __init__(self) -> None:
        pass

    def get_embedding_gen_ai(self, input, model="text-embedding-ada-002") -> str:
        response = embeddings.create(
        model_name=model,
        input=input
        )
        return response.data[0].embedding