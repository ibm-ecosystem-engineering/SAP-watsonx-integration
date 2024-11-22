from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from dotenv import load_dotenv
from app.route.rag import routes as rag_api
from fastapi.middleware.cors import CORSMiddleware
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

load_dotenv()

server_url = os.environ.get("SERVER_URL", default="http://localhost:3001")

app = FastAPI(
    title="SAP Rag pipeline",
    description="SAP Rag pipeline",
    version="1.0.1-rag-pipeline",
    servers=[
        {
            "url": server_url
        }
    ],
)

# Register the routes
app.include_router(rag_api.rag_api_route)

# Allow request from all origins 
origins = [ "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Entry point
if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=3001, reload=True)
