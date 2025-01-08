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
import re
import tika
tika.initVM()
from tika import parser 
import re
import pandas as pd
# Get embeddings

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

print(json.dumps(AICORE_CONFIG, indent=5))

HANA_DB_CONFIG = {
    "HOST": os.environ.get("HANA_DB_HOST"),
    "USER": os.environ.get("HANA_DB_USER"),
    "PASSWORD": os.environ.get("HANA_DB_PASSWORD"),
    "TABLE_NAME": os.environ.get("HANA_DB_TABLE_NAME")
}

# Parameters
parameters = {
    "ingestion_chunk_size": 256,
    "ingestion_chunk_overlap": 128
}

directory_path = os.environ.get("FILE_DIRECTORY_PATH")

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
# Create an AI API client instance
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

def get_filename(filename):
    filename = filename.replace(directory_path,"")
    return filename 

def pre_processingtext(text_data):
    replaced = re.sub("</?a[^>]*>", "", text_data)
    replaced = re.sub("</?head* />", "", replaced)
    replaced = re.sub("</?h*[^>]*>", "", replaced)
    replaced = re.sub("</?em*[^>]*>", "", replaced)
    replaced = re.sub("&amp;", "", replaced)
    return replaced

def remove_extra_lines(data):
    data =re.sub(r'\n\s*\n', '\n', data, flags=re.MULTILINE)
    return data
  
## get the files from specific folder
def get_all_files(folder_name):
    # Change the directory
    os.chdir(folder_name)
    # iterate through all file
    file_path_list =[]
    for file in os.listdir():
        #print(file)
        file_path = f"{folder_name}/{file}"
        file_path_list.append(file_path)
    return file_path_list

def extract_pdf_metadata_page(file_name):
    xml_data = parser.from_file(file_name, xmlContent=True)
    meta_data =xml_data['metadata']
    total_pages =0
    keywords =''
    title=''
    create_date =''
    modify_date =''
    if 'meta:page-count' in meta_data:
        total_pages = meta_data['meta:page-count']
        print(total_pages)
    if 'pdf:docinfo:title' in meta_data:
         title = meta_data['pdf:docinfo:title']
    if 'pdf:docinfo:keywords' in meta_data:
        keywords = meta_data['pdf:docinfo:keywords']
    if 'xmp:CreateDate' in meta_data:
        create_date = meta_data['xmp:CreateDate']
    if 'xmp:ModifyDate' in meta_data:
        modify_date = meta_data['xmp:ModifyDate']
    
    status = xml_data['status']
    if status == 200:
        content =xml_data['content']
    soup = BeautifulSoup(str(content), "html.parser")
    pages = soup.find_all("div", class_='page')
    total_pages = len(pages)
    file_name = get_filename(file_name).replace("/","")
    page_content =""
    doc_list =[]
    page_num =0
    for page in pages:
        page_num=page_num+1
        page_content = pre_processingtext(str(page))
        doc = {
                        "file_name":file_name,
                        "total_pages":total_pages,
                        "keywords":keywords,
                        "create_date":create_date,
                        "modify_date":modify_date,
                        "page_content":page_content,
                        "page_number":page_num,
                        "content_length":len(page_content)
                }
        doc_list.append(doc)
    return doc_list

file_path_list = get_all_files(directory_path)
len(file_path_list)
doc_list =[]
for file_name in file_path_list:
    print(file_name)
    doc_list.append(extract_pdf_metadata_page(file_name))


def preprocess_documents(documents):
    """Preprocess documents to extract content and metadata."""
    content = []
    metadata = []
    
    for doc in documents:
        document_url = doc.get("file_name", "")
        document_title = doc.get("file_name", "")

        page_content = doc.get("page_content", "")
        
        metadata.append({
            "title": document_title,
            "document_url": document_url,
            "page_number": doc.get("page_number", "")
        })

        content.append(f"Document Content: {page_content}")

    return content, metadata

# Load and preprocess documents
content, metadata = preprocess_documents(doc_list[0])

# Text splitter initialization
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=parameters["ingestion_chunk_size"],
    chunk_overlap=parameters["ingestion_chunk_overlap"],
    disallowed_special=()
)

# Split documents into chunks
split_docs = text_splitter.create_documents(content, metadatas=metadata)

# Generate unique document IDs
id_list = [hashlib.sha256(doc.page_content.encode()).hexdigest() for doc in split_docs]

# Log duplicate documents
duplicate_count = len(id_list) - len(set(id_list))
print(f"{duplicate_count} duplicate documents found.")
print(f"{len(set(id_list))} unique documents will be indexed into the vector store.")
print(100*"#")

# Function to write JSON data to a file
def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

doc_updated =[]
for doc in doc_list:
    for d in doc:
       doc_updated.append(d)

parsed_pdf_output_path = 'PDF_pagewise_data.json'  ## Change the output_file_path
write_json(doc_updated, parsed_pdf_output_path)

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
            doc.metadata.get('page_number', ''),
            doc.metadata.get('document_url', ''),
            doc.page_content,
            str(embed)
        ])
    except Exception as e:
        print(f"Error processing document {idx + 1}: {e}")

print(f"Total documents to index: {len(document_to_index)}")

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
        ID BIGINT, 
        TITLE NVARCHAR(100), 
        PAGE_NUMBER NVARCHAR(5), 
        URL NVARCHAR(100), 
        TEXT NCLOB, 
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
sql_insert = 'INSERT INTO ' + VECTOR_STORE_TABLE_NAME + '(ID, TITLE, PAGE_NUMBER, URL, TEXT, VECTOR_STR) VALUES (?,?,?,?,?,TO_REAL_VECTOR(?))'

cursor.executemany(sql_insert, document_to_index[0:])
print(f"{len(document_to_index)} documents inserted into the table.")
print(100*"#")

# Run vector search
def run_vector_search(query, metric="COSINE_SIMILARITY", k=4):
    try:
        query_vector = get_embedding(query)
        if query_vector is None:
            raise ValueError("Failed to generate query embedding.")

        sort_order = "DESC" if metric != "L2DISTANCE" else "ASC"
        sql_query = f"""
        SELECT TOP {k} ID, PAGE_NUMBER, TEXT
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
question="Overview of the Granite Pre-Training Dataset?"
print(f"Testing vector search, question = {question}")
print(100*"#")
# Test the vector search
try:
    context = run_vector_search(question, metric="COSINE_SIMILARITY", k=4)
    print(f"Search results: {context}")
except Exception as e:
    print(f"Error testing vector search: {e}")
print(100*"#")
