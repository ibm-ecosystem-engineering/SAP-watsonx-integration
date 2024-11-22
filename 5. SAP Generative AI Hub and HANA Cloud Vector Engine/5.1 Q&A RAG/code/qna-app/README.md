# Chatbot Interface for Q&A with RAG

This repository contains a Streamlit-based chatbot interface designed for Question-and-Answer (Q&A) use cases using Retrieval-Augmented Generation (RAG). The chatbot allows users to interact with a knowledge base, leveraging RAG to provide accurate and contextually relevant answers.

---

## Features

- **User-Friendly Interface**: Intuitive design for seamless user interaction.
- **RAG-Powered Responses**: Combines retrieval and generative models for enhanced Q&A performance.
- **Customizable Deployment**: Easy to configure and deploy locally or in a production environment.

---

## How to Run Locally

Follow the steps below to set up and run the chatbot interface on your local machine.

### Step 1: Clone the Repository

Clone or download the repository to your local system.

```bash  
git clone https://github.com/<user>/qna-app.git
cd qna-app
```

### Step 2: Update Environment Variables

Configure the `.env` file with the necessary environment variables to initialize the Streamlit app for Q&A. Use the provided example for guidance:

```bash  
cp env-example .env
```  

### Step 3: Set Up a Python Environment

Ensure Python (tested on Python 3.12) is installed on your system. Create and activate a virtual environment (optional but recommended):

```bash  
python3 -m venv venv
source venv/bin/activate
```  

### Step 4: Install Dependencies

Install all required Python packages using `requirements.txt`.

```bash  
pip install -r requirements.txt
```  

### Step 5: Run the Application

Launch the Streamlit app with the following command:

```bash  
streamlit run qna_streamlit_chat_app.py --server.port 8080  
```  

> **Note**: You can update the port number as needed by replacing `8080` with your desired port.  

### Step 6: Access the Application

Once the app is running, open your browser and navigate to the provided URL (e.g., `http://localhost:8080`).  

---

## How to Run it on Docker

Follow the steps below to package the application in a container image and run it on Docker.

> **Note**: You could run the same steps here on [Podman](https://podman.io/), if you simply alias the Docker CLI with the `alias docker=podman` shell command.

### Step 7: Build the Container Image

Build the container image using the provided `Dockerfile`. For example:

```bash
docker build --no-cache -t docker.io/<user>/qna-streamlit-app:latest .
```

Opetionally, you can push the container image to the registry, so that you can use it later on a different system:

```bash
docker push docker.io/<user>/qna-streamlit-app:latest
```

### Step 8: Run the Application

Launch the Streamlit app on Docker with the following command:  

```bash
docker run --rm --env-file .env -p 8080:8080 docker.io/<user>/qna-streamlit-app:latest
```

### Step 9: Access the Application

Once the app is running, open your browser and navigate to the provided URL (e.g., `http://localhost:8080`).  

---

## Additional Information  

- Ensure the `.env` file contains valid configurations for the app to function correctly.  
- This app can be easily extended to include custom RAG pipelines, datasets, or UI enhancements.  

Start interacting with your data like never before with this RAG-powered chatbot interface! 🚀  
