import os
import hashlib
import json
import warnings
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import S3DirectoryLoader
import boto3
from botocore.exceptions import ClientError

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Environment configuration
AICORE_CONFIG = {
    "AUTH_URL": os.environ.get("AICORE_AUTH_URL"),
    "CLIENT_ID": os.environ.get("AICORE_CLIENT_ID"),
    "CLIENT_SECRET": os.environ.get("AICORE_CLIENT_SECRET"),
    "RESOURCE_GROUP": os.environ.get("AICORE_RESOURCE_GROUP"),
    "BASE_URL": os.environ.get("AICORE_BASE_URL")
}

HANA_DB_CONFIG = {
    "HOST": os.environ.get("HANA_DB_HOST"),
    "USER": os.environ.get("HANA_DB_USER"),
    "PASSWORD": os.environ.get("HANA_DB_PASSWORD"),
    "TABLE_NAME": os.environ.get("HANA_DB_TABLE_NAME")
}

AWS_CONFIG = {
    "ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
    "SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
    "DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
    "BUCKET": os.environ.get("AWS_BUCKET"),
    "DOC_PATH_PREFIX": os.environ.get("AWS_DOC_PATH_PREFIX")
}

# Parameters
parameters = {
    "bucket": AWS_CONFIG["BUCKET"],
    "path_prefix": AWS_CONFIG["DOC_PATH_PREFIX"],
    "ingestion_chunk_size": 256,
    "ingestion_chunk_overlap": 128
}

import ssl
import urllib.request
ssl._create_default_https_context = ssl._create_unverified_context

print(100*"#")
print("downloading document from s3 bucket")
# Document loader
loader = S3DirectoryLoader(parameters["bucket"], prefix=parameters["path_prefix"])

# Text splitter initialization
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=parameters["ingestion_chunk_size"],
    chunk_overlap=parameters["ingestion_chunk_overlap"],
    disallowed_special=()
)

def preprocess_documents(documents):
    """Preprocess documents to extract content and metadata."""
    content = []
    metadata = []
    
    for doc in documents:
        document_url = ""
        document_title = doc.metadata.get("title", doc.metadata["source"].split("/")[-1].split(".")[0])

        if ".html" in doc.metadata["source"]:
            html_content = doc.page_content
            soup = BeautifulSoup(html_content, "html.parser")
            canonical_tag = soup.find("link", {"rel": "canonical"})
            title_tag = soup.find("title")

            if canonical_tag:
                document_url = canonical_tag.get("href")
            if title_tag:
                document_title = title_tag.get_text()

        metadata.append({
            "title": document_title,
            "source": doc.metadata["source"],
            "document_url": document_url,
            "page_number": doc.metadata.get("page", "")
        })

        content.append(f"Document Title: {document_title}\nDocument Content: {doc.page_content}")

    return content, metadata

# Load and preprocess documents
documents = loader.load()
content, metadata = preprocess_documents(documents)

# Split documents into chunks
split_docs = text_splitter.create_documents(content, metadatas=metadata)
print(f"{len(documents)} documents are split into {len(split_docs)} chunks with a chunk size of {parameters['ingestion_chunk_size']}.")

# Generate unique document IDs
id_list = [hashlib.sha256(doc.page_content.encode()).hexdigest() for doc in split_docs]

# Log duplicate documents
duplicate_count = len(id_list) - len(set(id_list))
print(f"{duplicate_count} duplicate documents found.")
print(f"{len(set(id_list))} unique documents will be indexed into the vector store.")
print(100*"#")

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
# Create an AI API client instance
#print(json.dumps(AICORE_CONFIG, indent=4))
try:
    ai_core_client = AICoreV2Client(
        base_url=AICORE_CONFIG["BASE_URL"],
        auth_url=AICORE_CONFIG["AUTH_URL"],
        client_id=AICORE_CONFIG["CLIENT_ID"],
        client_secret=AICORE_CONFIG["CLIENT_SECRET"]
    )

    # Get the number of GitHub repositories connected to SAP AI Core
    response = ai_core_client.repositories.query()
    print(f"Connected GitHub repositories: {response.count}")
except Exception as e:
    print(f"Error initializing AI Core client: {e}")
    exit(1)

print(100*"#")
# Get embeddings
from gen_ai_hub.proxy.native.openai import embeddings
# Helper function to fetch embeddings
def get_embedding(input_text, model="text-embedding-ada-002"):
    try:
        response = embeddings.create(
            model_name=model,
            input=input_text
            )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


# Prepare documents for indexing
document_to_index = []
for idx, doc in enumerate(split_docs):
    try:
        embed = get_embedding(doc.page_content)
        if embed is None:
            continue  # Skip documents with failed embeddings
        document_to_index.append([
            idx + 1,
            doc.metadata.get('title', ''),
            doc.metadata.get('source', ''),
            doc.metadata.get('page_number', ''),
            doc.metadata.get('document_url', ''),
            doc.page_content,
            str(embed)
        ])
    except Exception as e:
        print(f"Error processing document {idx + 1}: {e}")

print(f"Total documents to index: {len(document_to_index)}")

###print(str(document_to_index[0]))

VECTOR_STORE_TABLE_NAME=HANA_DB_CONFIG["TABLE_NAME"]
# Establish a secure connection to an SAP HANA database using hdbcli 
import hdbcli
from hdbcli import dbapi
# Establish a connection to HANA DB
# try:
connection = dbapi.connect(
    address=HANA_DB_CONFIG["HOST"],
    port=443,
    user=HANA_DB_CONFIG["USER"],
    password=HANA_DB_CONFIG["PASSWORD"],
    encrypt=True)

cursor = connection.cursor()

# Create the table if it doesn't exist
sql_create = f"""
    CREATE COLUMN TABLE {VECTOR_STORE_TABLE_NAME} (
        ID BIGINT PRIMARY KEY,
        TITLE NVARCHAR(200),
        SOURCE NVARCHAR(200),
        PAGE_NUMBER NVARCHAR(3),
        URL NVARCHAR(200),
        CONTENT NCLOB,
        VECTOR_STR REAL_VECTOR
    )
"""

print("Drop table if exists")
# SQL to drop the table
sql_drop_table = f"DROP TABLE {VECTOR_STORE_TABLE_NAME}"
try:
    cursor.execute(sql_drop_table)
    print(f"Table '{VECTOR_STORE_TABLE_NAME}' dropped successfully.")
except dbapi.Error as e:
    print(f"Error dropping table '{VECTOR_STORE_TABLE_NAME}': {e}")

try:
    cursor.execute(sql_create)
    print(f"Table '{VECTOR_STORE_TABLE_NAME}' created successfully.")
except dbapi.Error as e:
    print(f"Table creation skipped (likely already exists): {e}")

# Insert documents
sql_insert = 'INSERT INTO ' + VECTOR_STORE_TABLE_NAME + '(ID, TITLE, SOURCE, PAGE_NUMBER, URL, CONTENT, VECTOR_STR) VALUES (?,?,?,?,?,?,TO_REAL_VECTOR(?))'

cursor.executemany(sql_insert, document_to_index[0:])
print(f"{len(document_to_index)} documents inserted into the table.")
print(100*"#")
    # Commit the transaction
    # connection.commit()
#except dbapi.Error as e:
#    print(f"Database error: {e}")
#    exit(1)


# Run vector search
def run_vector_search(query, metric="COSINE_SIMILARITY", k=4):
    try:
        query_vector = get_embedding(query)
        if query_vector is None:
            raise ValueError("Failed to generate query embedding.")

        sort_order = "DESC" if metric != "L2DISTANCE" else "ASC"
        sql_query = f"""
        SELECT TOP {k} ID, CONTENT 
        FROM {VECTOR_STORE_TABLE_NAME}
        ORDER BY {metric}(VECTOR_STR, TO_REAL_VECTOR('{query_vector}')) {sort_order}
        """
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error during vector search: {e}")
        return []

print(100*"#")
question="how to perform sql optimization?"
print(f"Testing vector search, question = {question}")
print(100*"#")
# Test the vector search
try:
    context = run_vector_search(question, metric="COSINE_SIMILARITY", k=4)
    print(f"Search results: {context}")
except Exception as e:
    print(f"Error testing vector search: {e}")
print(100*"#")