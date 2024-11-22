import streamlit as st
from pydantic import BaseModel
import requests
import uuid
import os
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up configuration variables
aicore_resource_group = os.getenv('RESOURCE_GROUP') or "default"
backend_url = os.getenv('DEPLOYMENT_URL') + '/v2/generate'

# Initialize the AI Core API client
ai_core_client = AICoreV2Client(
    base_url=os.getenv('AI_API_URL') + '/v2',
    auth_url=os.getenv('AUTH_URL') + '/oauth/token',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

# Define the theme for the dashboard
DASHBOARD_THEME = {
    "theme.base": "light",
    "theme.backgroundColor": "#F4F4F4",
    "theme.primaryColor": "#5591f5",
    "theme.secondaryBackgroundColor": "#D1D1D1",
    "theme.textColor": "#0a1464"
}

# Apply the theme to the Streamlit app
for theme_key, theme_val in DASHBOARD_THEME.items():
    if theme_key.startswith("theme"):
        st._config.set_option(theme_key, theme_val)

# Define the structure of a chat message using Pydantic
class MsgEntry(BaseModel):
    id: str
    role: str = 'assistant'
    text: str = 'write'
    documents: list[dict] = []
    show_documents: bool = False
    log_id: str = ''
    rating_options: int = 5

# Function to call the backend API and retrieve a response
def get_response(prompt):
    """
    Send a query to the backend and retrieve the response.
    Returns the bot's response text, associated documents, and log ID.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": ai_core_client.rest_client.get_token(),
            "AI-Resource-Group": aicore_resource_group
        }
        data = {"query": prompt}
        response = requests.post(backend_url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("response", ""), response_json.get("documents", []), response_json.get("log_id", "")
    except requests.RequestException as e:
        st.error(f"Error fetching response: {e}")
        return "Error retrieving response.", [], ""

# Function to toggle the visibility of documents for a specific message
def toggle_document_visibility(id):
    """
    Toggle the `show_documents` attribute of a message with the given ID.
    """
    for msg in st.session_state.history:
        if msg.id == id:
            msg.show_documents = not msg.show_documents
            break

# Function to render a single chat message
def render_message(msg, save=False):
    """
    Display a chat message in the app.
    Optionally, save it to the session state history.
    """
    with st.chat_message(msg.role):
        # Display the main message text
        st.markdown(msg.text)

        # Display associated documents if toggled
        if msg.show_documents:
            if msg.documents:
                doc_table = "<table><thead><tr><th>Title/Source</th><th>Document</th></tr></thead><tbody>"
                for doc in msg.documents:
                    doc_table += f"""
                    <tr>
                        <td><a href="{doc['metadata']['document_url']}">{doc['metadata']['title']}</a></td>
                        <td>{doc['page_content']}</td>
                    </tr>
                    """
                doc_table += "</tbody></table>"
                st.markdown(doc_table, unsafe_allow_html=True)
            else:
                st.markdown("No documents were used.")

        # Save the message to history if specified
        if save:
            st.session_state.history.append(msg)

# Function to reset the chat history
def reset_chat():
    """Clear the chat history and display the default welcome message."""
    st.session_state.history = [MsgEntry(id=str(uuid.uuid4()), text="Hi! How can I help you today?")]

# Configure the Streamlit page
st.set_page_config(page_title="QnA with RAG Bot", layout="wide")
st.title("Q&A RAG Interactive UI")

# Initialize session state for chat history
if "history" not in st.session_state:
    reset_chat()

# Layout for additional options (reset button and feedback, if any)
_, _, reset_col = st.columns([0.6, 0.2, 0.2])

# Reset button
if reset_col.button("Reset Chat"):
    reset_chat()

# Render chat history
for message in st.session_state.history:
    render_message(message)

# Input box for the user to enter their query
user_input = st.chat_input("Type your question here...")
if user_input:
    # Create a new user message
    user_msg = MsgEntry(id=str(uuid.uuid4()), role="user", text=user_input)
    render_message(user_msg, save=True)

    # Fetch and display the bot's response
    bot_text, documents, log_id = get_response(user_input)
    bot_msg = MsgEntry(id=str(uuid.uuid4()), role="assistant", text=bot_text, documents=documents, log_id=log_id)
    render_message(bot_msg, save=True)
