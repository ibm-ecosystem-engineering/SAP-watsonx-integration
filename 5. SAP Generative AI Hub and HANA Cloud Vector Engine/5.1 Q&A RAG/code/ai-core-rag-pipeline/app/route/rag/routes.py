import json
import logging
import time
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security, requests as request
import os
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.security import APIKeyHeader
from app.src.model.LLMOutput import LLMOutput
from app.src.model.LLMInput import LLMInput
from app.src.services.embedding import Embedding
from app.src.services.hanadb import HanaDB
from app.src.services.llmservice import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

load_dotenv()

rag_api_route = APIRouter()

AICORE_AUTH_URL=os.environ.get("AICORE_AUTH_URL")
AICORE_CLIENT_ID=os.environ.get("AICORE_CLIENT_ID")
AICORE_CLIENT_SECRET=os.environ.get("AICORE_CLIENT_SECRET")
AICORE_RESOURCE_GROUP=os.environ.get("AICORE_RESOURCE_GROUP")
AICORE_BASE_URL=os.environ.get("AICORE_BASE_URL")
HANA_DB_HOST=os.environ.get("HANA_DB_HOST")
HANA_DB_USER=os.environ.get("HANA_DB_USER")
HANA_DB_PASSWORD=os.environ.get("HANA_DB_PASSWORD")
HANA_DB_TABLE_NAME=os.environ.get("HANA_DB_TABLE_NAME")

hana_db: HanaDB = HanaDB(
    HANA_DB_HOST,
    HANA_DB_USER,
    HANA_DB_PASSWORD,
    HANA_DB_TABLE_NAME  
)
embdedding: Embedding = Embedding()

API_PREFIX = "/v2"

## This routes returns the text to SQL from a given context and a sql query
@rag_api_route.get(API_PREFIX + "/status")
def root_api_v2():
    return {
        "msg": "status working!"
    }

@rag_api_route.post(API_PREFIX + "/generate")
def llm_generate(llm_input: LLMInput) -> LLMOutput:
    info = {}
    tic = time.perf_counter()
    query = llm_input.query

    ## Step 1: Get the question/query embedding
    query_embedding = embdedding.get_embedding_gen_ai(query)
    toc = time.perf_counter()
    info["embedding_time"] = toc - tic

    tic = time.perf_counter()

    ## Step 2: Getting LLM Service Instance
    llm_service = LLMService(hana_db)

    ## Step 3: LLM Generation
    llm_response = llm_service.generate(query, query_embedding)

    print(llm_response)

    toc = time.perf_counter()
    info["llm_response_time"] = toc - tic
    logging.info(json.dumps(info, indent=4))
    return LLMOutput(response=llm_response)

