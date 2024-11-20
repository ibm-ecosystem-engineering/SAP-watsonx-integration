import streamlit as st
from pydantic import BaseModel
import requests
import time
import uuid
import os
import re
import json
from dotenv import dotenv_values
# Load AI Core Client Library
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

server_config = dotenv_values(".env")

# Set your SAP AI Core credential
client_id = server_config["CLIENT_ID"]
client_secret = server_config["CLIENT_SECRET"]
base_url = server_config["AI_API_URL"] + '/v2'
auth_url = server_config["AUTH_URL"] + '/oauth/token'

# Create a client connection
ai_core_client = AICoreV2Client(
    base_url = base_url,
    auth_url = auth_url,
    client_id = client_id,
    client_secret = client_secret
)

#######################
#theme configuration
dashboard_theme= {
    "theme.base": "light",
    "theme.backgroundColor": "#F4F4F4",
    "theme.primaryColor": "#5591f5",
    "theme.secondaryBackgroundColor": "#D1D1D1",
    "theme.textColor": "#0a1464"
}

for theme_key, theme_val in dashboard_theme.items(): 
    if theme_key.startswith("theme"): st._config.set_option(theme_key, theme_val)

# read default RAG function credentials from environment
if not 'QNA_RAG_APIKEY' in st.session_state:
    try:
        st.session_state.QNA_RAG_APIKEY = server_config['QNA_RAG_APIKEY']
    except:
        st.session_state.QNA_RAG_APIKEY = ''

if not 'QNA_RAG_DEPLOYMENT_URL' in st.session_state:
    try:
        st.session_state.QNA_RAG_DEPLOYMENT_URL = server_config['QNA_RAG_DEPLOYMENT_URL']
    except:
        st.session_state.QNA_RAG_DEPLOYMENT_URL = ''

# set recommendation 
sample_recommendation=""
if server_config['IsExpertSample'] == "Yes":
    sample_recommendation="This is sample expert recommendation!,"

# model for single chat message
class msg_entry(BaseModel):
    id: str
    role: str = 'assistant'
    text: str = 'write'
    documents: list[dict] = []
    show_documents: bool = False
    log_id: str = ''
    rating_options: int = 5

# retrieve and cache IAM access token
AccessToken = ''
AccessTokenExpires = 0
def get_token(force=False):
    global AccessToken, AccessTokenExpires
    now = time.time()
    if AccessTokenExpires <= now or force:

        if not api_key or not endpoint_url:
            st.error("Please provide RAG function credentials.")
            return ''

        # get access token
        response = requests.post('https://iam.cloud.ibm.com/identity/token', data={'apikey': api_key, 'grant_type': 'urn:ibm:params:oauth:grant-type:apikey'})
        if response.status_code == 200:
            resp = response.json()
            if not 'access_token' in resp:
                st.error("Unexpected token format.")
                return ''
        
            AccessToken = resp['access_token']
            # calculate expiration time (as a precaution, subtract 5 minutes)
            AccessTokenExpires = ( now + resp['expires_in'] if 'expires_in' in resp else ( resp['expiration'] if 'expiration' in resp else now ) ) - 300

    return AccessToken


# call RAG function
## TODO ----
def exec_request(payload, ignore_errors=False):
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + get_token()}
    status_code = 0
    try:
        response = requests.post(endpoint_url, json=payload, headers=header)
        status_code = response.status_code
        if not status_code == 200 and not ignore_errors:
            st.error(f"Error with status code: {status_code}")
    except:
        st.error(f"Connecting RAG function failed.")
        response = None

    return response


# run RAG function to generate response
def get_response(prompt):
    
    endpoint = server_config["BACKEND_URL"]
    headers = {"Content-Type": "application/json",
            "Authorization": ai_core_client.rest_client.get_token(),
            "AI-Resource-Group": "genai-demo"}
    data = {
        "query": prompt
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))

    response = response.text
    response = json.loads(response)
    #print('*'*80)
    #print(response)
    #print('*'*80)
    return str(response["response"]), "documents", ''


# run RAG function to update feedback 
def send_feedback(log_id, value, comment=None):
    st.session_state.active = ''
    
    if not log_id == '':
        feedback_Value=int(value)
        if feedback_Value < 100 and comment == None:
            st.session_state.feedback = value
            st.session_state.log_id = log_id
            new_msg = msg_entry(id=str(uuid.uuid4()), role='assistant', text='Thanks for your feedback! Please add a comment.')
            st.session_state.history.append(new_msg)
            return None
        else:
            response_update = exec_request({"input_data": [{"fields": ["log_id", "value", "comment"], "values": [[log_id, value, comment if not comment == None else '']]}]})
            if feedback_Value < 100:
                new_msg = msg_entry(id=str(uuid.uuid4()), role='assistant', \
                text='Thanks! Feedback has been sent. \n If you want to know better answer for this question, Please click on above expert recommendation!' if response_update.status_code == 200 and response_update.json()['predictions'][0]['values'][0][0] == 'ok' else 'Feedback update got failed. If you need experts on this question, click on above expert recommendations!')
                st.session_state.expert_disabled=False
                st.button('Recommended Expert for this question', 'expert_toggle'+new_msg.id, on_click=get_expert_recommendation, args=(log_id,),disabled=st.session_state.expert_disabled)
            else: 
                new_msg = msg_entry(id=str(uuid.uuid4()), role='assistant', \
                text='Thanks! Feedback has been sent. \n Type your next question in input box.' if response_update.status_code == 200 and response_update.json()['predictions'][0]['values'][0][0] == 'ok' else 'Feedback update got failed. Type your next Question in input box')
            if comment == None:
                st.session_state.history.append(new_msg)
                return None
            else:
                return new_msg

# run RAG function to get expert recommendation 
def get_expert_recommendation(log_id):
    st.session_state.active = ''
    st.session_state.expert_recommendation = ''
    if not log_id == '':
        response_update = exec_request({"input_data": [{"fields": ["_function", "log_id"], "values": [["recommend_top_experts", log_id]] }]})
        print(f"response is {response_update.json()}")
        expert_msg = msg_entry(id=str(uuid.uuid4()), role='assistant', \
            text=sample_recommendation+' Please contact expert '+response_update.json()['predictions'][0]['values'][0][0][0]["name"] + ' , Email id: '+ response_update.json()['predictions'][0]['values'][0][0][0]["email"] + " to know more details. \n Please ask Next Question!" if response_update.status_code == 200 and 'expert_details' in response_update.json()['predictions'][0]['values'][0][1] else 'No Experts found on this topic, Please ask next Question!')
            
        # text='Please contact expert '+response_update.json()['predictions'][0]['values'][0][0][0]["name"] + ' , Email id: '+ response_update.json()['predictions'][0]['values'][0][0][0]["email"] + 'Profile Info: '+ response_update.json()['predictions'][0]['values'][0][0][0]["text"] if response_update.status_code == 200 and response_update.json()['predictions'][0]['values'][0][1] == 'expert_details retrieved from log records' else 'No Experts found on this topic')
        st.session_state.expert_disabled=True
        st.session_state.history.append(expert_msg)
        
    return None

# ping RAG function
def ping():
    response_ping = exec_request({"input_data": [{"fields": [""], "values": [[""]] }]}, ignore_errors=True)
    status_code = response_ping.status_code if not response_ping == None else 0
    if not status_code == 200:
        return False, status_code 
    response = response_ping.json()
    # expected response: {'predictions': [{'fields': ['status'], 'values': [['invalid parameters']]}]}
    return 'predictions' in response and len(response['predictions']) > 0 and len(response['predictions'][0]['fields']) > 0 and response['predictions'][0]['fields'][0] == 'status', status_code


def get_msg_by_id(id):
    if not 'history' in st.session_state:
        return None
    hits = [index for index in range(len(st.session_state.history)) if st.session_state.history[index].id == id]
    return st.session_state.history[hits[0]] if len(hits) > 0 else None

# toggle displaying documents in chat message
def show_hide_documents(id):
    hits = [index for index in range(len(st.session_state.history)) if st.session_state.history[index].id == id]
    if len(hits) > 0:
        st.session_state.history[hits[0]].show_documents = not st.session_state.history[hits[0]].show_documents


# print single chat message
def print_message(msg: msg_entry, save=False):
    with st.chat_message(msg.role):
        st.markdown(msg.text)
        if msg.show_documents:
            m = f''
            if len(msg.documents) > 0:
                m = f'{m}<table><thead><th>Title/Source</th><th style="text-align: center;">Document</th></thead><tbody>'
                
                for d in msg.documents:
                    m = f'{m}<tr><td><a href="{d["metadata"]["document_url"]}">{d["metadata"]["title"]}</a></td><td style="text-align: left;">{d["page_content"]}</td></tr>'
                
                m = f'{m}</tbody></table><br><br><hr>'
            else:
                m = f'{m}No documents were used.'
            st.markdown(m,unsafe_allow_html=True)
        if not msg.log_id == '':
            disabled = not msg.id == st.session_state.active
            st.session_state.expert_disabled = True
            cols = st.columns([1 for _ in range(msg.rating_options)] + [9 - msg.rating_options])
            #                0      1      2     3      4    5-ok    6     7      8
            options_list = ['👎', '👍', '😡', '😠', '🙁', '😐', '🙂', '😀', '🤩']
            options_selector = [[0,1],[3,5,7],[2,3,7,8],[2,3,5,7,8]]
            for _i in range(msg.rating_options-1, -1, -1):
                cols[msg.rating_options-_i-1].button(options_list[options_selector[msg.rating_options-2][_i]], f"opt{str(_i)}{msg.id}", \
                                on_click=send_feedback, args=(msg.log_id,str(round(100*(_i/(msg.rating_options-1)))),), disabled=disabled)
            st.button(('Hide' if msg.show_documents else 'Show') + ' source documents', 'toggle'+msg.id, on_click=show_hide_documents, args=(msg.id,))
    if save:
        st.session_state.history.append(msg)



##########################################################################################
## Refresh page

# feedback value to be sent after comment imput
if not 'feedback' in st.session_state:
    st.session_state.feedback = ''

# current log id
if not 'log_id' in st.session_state:
    st.session_state.log_id = ''

# msg id with active feedback buttons
if not 'active' in st.session_state:
    st.session_state.active = ''

# default feedback rating options
if not 'rating_options' in st.session_state:
    st.session_state.rating_options = int(server_config["DEFAULT_FEEDBACK_RATING_OPTIONS"])

if not 'max_rating_options' in st.session_state:
    st.session_state.max_rating_options = int(server_config["MAX_FEEDBACK_RATING_OPTIONS"])

api_key=st.session_state.QNA_RAG_APIKEY
endpoint_url=st.session_state.QNA_RAG_DEPLOYMENT_URL

st.set_page_config(page_title='QnA with RAG Bot', layout = "wide")
st.title("Q&A RAG interactive UI with streamlit based app")
st.session_state.connection=False

ok, status_code = ping()
if ok:
    st.session_state.connection=True
else:
    ##st.error(f"Connection test failed, status code: {str(status_code)}")
    st.session_state.connection=True

_sub_title_description , _feedback_slider, _reset_button = st.columns([0.60,0.20,0.10], gap="large")

if not st.session_state.connection:
    _sub_title_description.error("This dashboard cannot be generated! Please configure your app with deployment function properly! Contact Adminstrator")
    st.stop()
else:
    match = re.search(r'/deployments/([^/]*)/', st.session_state.QNA_RAG_DEPLOYMENT_URL)
    ##_sub_title_description.markdown("This is QnA Chat Bot - Retrieval Augmented Generation by calling deployment function "+ f"**{match.group(1)}**" + " of watsonx.ai aaS" )
    _sub_title_description.markdown(f"\n Rating options slider is set to default {st.session_state.rating_options} options, please feel free to change it!. To clear chat history, click on reset chat button on the right side" )

## maximum of 5 feedback ratings are allowed

if _reset_button.button('Reset chat'):
    if 'history' in st.session_state:
        del st.session_state.history

# chat history (with welcome message)
if not 'history' in st.session_state:
    st.session_state.history = [msg_entry(id=str(uuid.uuid4()), role='assistant', \
        text="Hi there! I am a chat bot, please type your question in below input box!")]

# user's input
if prompt := st.chat_input("Post your Question here to RAG Chat Bot!"):

    # print chat (all feedback buttons inactive)
    st.session_state.active = ''
    for _msg in st.session_state.history:
        print_message(_msg)

    new_msg = msg_entry(id=str(uuid.uuid4()), role='user', text=prompt)
    print_message(new_msg, save=True)

    if not st.session_state.feedback == '':
        # update feedback
        new_msg = send_feedback(st.session_state.log_id, st.session_state.feedback, prompt)
        st.session_state.feedback = ''
    #elif not st.session_state.recommendation == '':

    else:
        # run RAG function
        text, documents, log_id = get_response(prompt)
        new_msg = msg_entry(id=str(uuid.uuid4()), role='assistant', text=text)

    st.session_state.active = new_msg.id if not new_msg.log_id == '' else ''
    print_message(new_msg, save=True)

else:
    # print chat (with active feedback button)
    for _msg in st.session_state.history:
        print_message(_msg)
