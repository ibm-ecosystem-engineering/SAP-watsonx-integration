# Document Indexing to SAP HANA Vector Database  

This guide demonstrates the process of indexing documents in the SAP HANA vector database. Follow the steps below to set up the application and get started.  

---

## Overview  

### Key Components  
- **Documents for Indexing**: A collection of files (e.g., DOCX, PDF, HTML) to be indexed.  
- **Cloud Object Storage (COS)**: Stores documents prior to indexing.  
- **Embedding Model**: Used for vectorizing documents (e.g., the ADDA model).  
- **HANA Database Instance**: Hosts the indexed data for efficient retrieval.  

---

## Running the Application Locally  

### Step 1: Set Up the Environment  

Create a virtual environment to isolate dependencies.  

```bash
python3 -m venv backend  
source backend/bin/activate  
```  

### Step 2: Install Dependencies  

Install the required Python packages using the provided `requirements.txt` file.  

```bash
pip3 install -r requirements.txt  
```  

### Step 3: Configure Environment Variables  

Create a `.env` file and populate it with the necessary credentials and configurations. Use the provided `env` template as a reference.  

```bash
cp env .env  
```  

#### Example `.env` Variables  

```dotenv  
## AI Core Configuration  
AICORE_AUTH_URL="https://***.authentication.***.hana.ondemand.com"  
AICORE_CLIENT_ID="sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!xxxxxxx|aicore!xxxx"  
AICORE_CLIENT_SECRET="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$***"  
AICORE_RESOURCE_GROUP="***"  
AICORE_BASE_URL="https://api.ai.***.hana.ondemand.com"  

## HANA Database Credentials  
HANA_DB_HOST="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.***.***.hanacloud.ondemand.com"  
HANA_DB_USER="***"  
HANA_DB_PASSWORD="***"  
HANA_DB_TABLE_NAME="***"  

## AWS Cloud Object Storage  
AWS_ACCESS_KEY_ID="***"  
AWS_SECRET_ACCESS_KEY="***"  
AWS_DEFAULT_REGION="***"  
AWS_BUCKET="***"  
AWS_DOC_PATH_PREFIX="***"  
```  

### Step 4: Start the Application  

Run the application server.  

```bash  
python3 main.py  
```  

---

## Running with Docker  

### Step 1: Build the Docker Image  

Build a Docker image using the provided `Dockerfile`.  

```bash  
docker build -t <DOCKER_REGISTRY>/<NAMESPACE>:<TAG> .  
```  

### Step 2: Publish the Docker Image  

Push the Docker image to your container registry.  

```bash  
docker push <DOCKER_REGISTRY>/<NAMESPACE>:<TAG>  
```  

### Step 3: Run the Docker Container  

Ensure all environment variables are defined in the `env` file before running the container.  

```bash  
podman run --rm --env-file ./env <DOCKER_REGISTRY>/<NAMESPACE>:<TAG>  
```  
