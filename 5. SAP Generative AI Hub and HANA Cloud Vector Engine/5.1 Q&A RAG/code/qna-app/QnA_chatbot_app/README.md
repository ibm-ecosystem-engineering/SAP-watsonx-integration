
## Chatbot Interface for QnA with RAG

This Streamlit app provides a chatbot interface for a QnA usecase.

### How to Run locally

1. Clone or download this repository.
2. Navigate to the project directory QnA_chatbot_app
3. Update env file to initialize the streamlit app for QnA and `cp env .env`
4. Make sure you have python environment available.
5. Create a virtual environment and activate it (optional):
   
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. Run the app:
   ```bash
   streamlit run qna_streamlit_chat_app.py --server.port 8080
   ```
   Note: update port number accordingly
   
8. Open the app in your browser using the provided URL.
