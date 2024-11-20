# Document indexing to SAP Hana Vector database

The instruction demonstrate the document indexing to SAP hana vector database.

## Components

- Document to index
- Cloud Object Storage to store the documents for indexing
- Embedding model ( We are suing adda model here)
- Hana db instance

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
cp env .env
```

```sh
## AICORE configuration data
AICORE_AUTH_URL="https://***.authentication.***.hana.ondemand.com"
AICORE_CLIENT_ID="sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!xxxxxxx|aicore!xxxx"
AICORE_CLIENT_SECRET="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$***"
AICORE_RESOURCE_GROUP="***"
AICORE_BASE_URL="https://api.ai.***.hana.ondemand.com"

## Hana db credentials
HANA_DB_HOST="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.***.***.hanacloud.ondemand.com"
HANA_DB_USER="***"
HANA_DB_PASSWORD="***"

HANA_DB_TABLE_NAME="***"

## AWS COS credentials
AWS_ACCESS_KEY_ID="***"
AWS_SECRET_ACCESS_KEY="***"
AWS_DEFAULT_REGION="***"
AWS_BUCKET="***"
AWS_DOC_PATH_PREFIX="***"
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

### Run

Before you run the container please fillup all the required environment variables in the file `env` provided with the code.

```sh
podman run --rm --env-file ./env <DOCKER_REGISTRY>/<NAME_SPACE>:<TAG>
```