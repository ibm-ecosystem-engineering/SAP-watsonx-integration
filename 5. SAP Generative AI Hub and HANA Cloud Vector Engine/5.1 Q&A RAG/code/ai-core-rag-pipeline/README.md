# SAP Q&A RAG Pipeline

This application is an SAP Q&A RAG Pipeline that uses the following components and workflow to generate LLM responses:

- **Embedding Model**: Generates an embedding for the query.
- **SAP HANA Vector DB**: Performs a semantic query to retrieve relevant documents from the HANA Vector database, building the context.
- **Prompt Construction**: Uses the retrieved context to build a prompt for the LLM.
- **LLM (Granite Model)**: Generates a response based on the provided prompt.

## Run the application locally

### Create environment

```sh
python3 -m venv backend
```

```sh
source backend/bin/activate
```

### Install requirement

```sh
pip3 install -r requirements.txt
```

### Run the server

Create a `.env` file and fill up the below variables to make the application running.

```sh
## AICORE configuration data
AICORE_AUTH_URL=""
AICORE_CLIENT_ID=""
AICORE_CLIENT_SECRET=""
AICORE_RESOURCE_GROUP=""
AICORE_BASE_URL=""
ORC_API_URL=""

## Hana db credentials
HANA_DB_HOST=""
HANA_DB_USER=""
HANA_DB_PASSWORD=""
HANA_DB_TABLE_NAME=""
```

### Run the application

```sh
python3 main.py
```

## Docker container

### Build

```sh
docker build -t <DOCKER_REGISTRY>/<NAME_SPACE>:<TAG> .
```

### Publish

```sh
docker push <DOCKER_REGISTRY>/<NAME_SPACE>:<TAG>
```

Take a note of the docker container you push to your repo. it will be needed in the SAP-AI Core workflow to serve the application.
