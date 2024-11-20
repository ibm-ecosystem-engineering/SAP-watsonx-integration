# SAP Q&A RAG Pipeline  

This application implements a **SAP Q&A Retrieval-Augmented Generation (RAG) Pipeline**, integrating advanced components to deliver accurate responses using a Large Language Model (LLM).  

---

## Workflow Overview  

1. **Embedding Model**:  
   - Encodes the query into a vector representation for semantic matching.  

2. **SAP HANA Vector Database**:  
   - Executes a semantic search to retrieve relevant documents, constructing a context for the query.  

3. **Prompt Construction**:  
   - Combines the retrieved context with the query to create a prompt for the LLM.  

4. **LLM (Granite Model)**:  
   - Generates the final response based on the constructed prompt.  

---

## Running the Application Locally  

Follow these steps to set up and run the application on your local machine.  

### Step 1: Set Up the Python Environment  

Create and activate a virtual environment to manage dependencies:  

```bash  
python3 -m venv backend  
source backend/bin/activate  
```  

### Step 2: Install Dependencies  

Install the required Python packages:  

```bash  
pip3 install -r requirements.txt  
```  

### Step 3: Configure Environment Variables  

Create a `.env` file and populate it with the necessary credentials and configurations:  

```bash  
## AI Core Configuration  
AICORE_AUTH_URL=""  
AICORE_CLIENT_ID=""  
AICORE_CLIENT_SECRET=""  
AICORE_RESOURCE_GROUP=""  
AICORE_BASE_URL=""  
ORC_API_URL=""  

## HANA Database Configuration  
HANA_DB_HOST=""  
HANA_DB_USER=""  
HANA_DB_PASSWORD=""  
HANA_DB_TABLE_NAME=""  
```  

### Step 4: Run the Application  

Start the application server:  

```bash  
python3 main.py  
```  

---

## Using Docker  

### Step 1: Build the Docker Image  

Build the Docker image using the provided `Dockerfile`:  

```bash  
docker build -t <DOCKER_REGISTRY>/<NAMESPACE>:<TAG> .  
```  

### Step 2: Publish the Docker Image  

Push the built image to your container registry:  

```bash  
docker push <DOCKER_REGISTRY>/<NAMESPACE>:<TAG>  
```  

> **Note**: Save the container image details for use in the SAP AI Core workflow to deploy and serve the application.  

---

## Next Steps  

- **Integration with SAP AI Core**:  
  - Use the published Docker container in SAP AI Core workflows to enable seamless deployment and inference.  
- **Customization**:  
  - Extend the pipeline by integrating additional models, enhancing prompt construction, or fine-tuning the Granite model.  

Harness the power of semantic search and LLMs to build smarter and more efficient Q&A solutions with SAP's Q&A RAG Pipeline! 🚀
