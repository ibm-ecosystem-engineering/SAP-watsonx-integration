# Indexing Documents with SAP HANA Cloud Vector Engine

This guide demonstrates the process of indexing documents with SAP HANA Cloud Vector Engine. Follow the step-by-step instructions below to get started.

---

## Overview

### Key Components
- **Documents for Indexing**: A collection of files (e.g., DOCX, PDF, HTML) to be indexed
- **Cloud Object Storage (AWS S3)**: Stores documents prior to indexing
- **Embedding Model**: Used for vectorizing documents (e.g., the ADDA model)
- **HANA Database Instance**: Hosts the indexed data for efficient retrieval

---

## How to Run Locally

You can follow the steps below to run the Python script `app.py` directly.

### Step 1: Set Up a Virtual Environment

Create a Python virtual environment to isolate dependencies.

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

Create a `.env` file and populate it with the necessary credentials and configurations, using the provided `env-example` file as a reference. More details can be found in the example file.

```bash
cp env-exsample .env
```  

### Step 4: Start the Application  

Run the application server.  

```bash  
python3 app.py
```  

---

## Run it on Docker

Alternatively, you can package the Python script in a container image and run it on Docker.

> **Note**: You could run the same steps here on [Podman](https://podman.io/), if you simply alias the Docker CLI with the `alias docker=podman` shell command.

### Step 5: Build the Container Image

Build the container image using the provided `Dockerfile`. For example:

```bash
docker build --no-cache -t docker.io/<user>/docs-indexing:latest .
```

Optionally, you can push the container image to the registry, so that you can use it later on a different system:

```bash
docker push docker.io/<user>/docs-indexing:latest
```

### Step 6: Run it on Docker

Ensure all environment variables are properly defined in the `.env` file before running the container.

```bash
docker run --rm --env-file .env docker.io/<user>/docs-indexing:latest
```
