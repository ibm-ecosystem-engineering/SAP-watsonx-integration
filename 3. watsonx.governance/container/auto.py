#!/bin/python3
import os
import joblib
import pandas as pd
import json
from flask import Flask, jsonify, request
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson_openscale import APIClient
from ibm_watson_openscale.supporting_classes.enums import DataSetTypes, TargetTypes
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load the machine learning model
model = joblib.load("scikit_model.pkl")

# Use environment variables to set credentials for OpenScale connection
openscale_creds = os.getenv('OPENSCALE_CREDS')
openscale_creds_json = json.loads(openscale_creds)
ibmcloudapikey = openscale_creds_json["cloudapikey"]
SERVICE_INSTANCE_ID = openscale_creds_json["service_instance_id"]
subscription_id = openscale_creds_json["subscription_id"]
service_url = openscale_creds_json["service_url"]

# Default method to check if the endpoint is active
@app.route("/", methods=["GET"])
def default():
    return "This REST API call makes employee promotion predictions.\nUse POST /v2/predict with your payload to make predictions. \nUse POST /v2/predict_and_log with your payload to make predictions and then store request and response data to payload logging and feedback logging tables.\nUse POST /v2/feedback_logging with your payload and response to load data into Watson OpenScales feedback_logging table.\nUse POST /v2/payload_logging with your payload to load data and response into Watson OpenScales payload_logging table."

# Sample get method to check if the model is loaded 
@app.route("/v2/greet", methods=["GET"])
def status():
    global model
    if model is None:
        return "Flask Code: Model was not loaded."
    else:
        return "Flask Code: Model is loaded."

# The function to read and process input data, make predictions and return output as a json.
def predict(payload):

    global model
    payload = payload['input_data'][0]
    df = pd.DataFrame(payload['values'], columns=payload['fields'])
    # Check if the column exists
    if 'is_promoted' in df.columns:
    # Remove the column
        df = df.drop(columns=['is_promoted'])
    try:
        probs = model.predict_proba(df.values).tolist()
        preds = model.predict(df.values).tolist()
        res = [{'prediction': preds[i], 'probability': probs[i]} for i in range(len(preds))]
        output = {
            'predictions': [{
                "fields": ['prediction', 'probability'],
                "values": [[res[i]['prediction'], res[i]['probability']] for i in range(len(res))]
            }]
        }
    except ValueError as e:
        
        probs = model.predict_proba(df).tolist()
        preds = model.predict(df).tolist()
        res = [{'prediction': preds[i], 'probability': probs[i]} for i in range(len(preds))]
        output = {
            'predictions': [{
                "fields": ['prediction', 'probability'],
                "values": [[res[i]['prediction'], res[i]['probability']] for i in range(len(res))]
            }]
        }
    except Exception as e:
        print(f"Error during prediction: {e}")
        output = {"ERROR": "Prediction Failed"}
    return output


# POST /v2/predict to make predictions and return output as a json.  
@app.route("/v2/predict", methods=["POST"])
def predict_employee_promotion_response():

    payload = request.get_json()
    try:    
        output=predict(payload)
    except Exception as e:
        print(f"Error during prediction: {e}")
        output = {"ERROR": "Prediction Failed"}
    return jsonify(output)

# POST /v2/authenticate to authenticate to watson openscale and return watson openscale client
@app.route("/v2/authenticate", methods=["POST"])
def openscale_authentication():
    try:
        service_credentials = {
        "apikey": ibmcloudapikey,
        "url": service_url
        }

        authenticator = IAMAuthenticator(
                apikey=service_credentials["apikey"],
                url="https://iam.cloud.ibm.com/identity/token"
            )

        wos_client = APIClient(authenticator=authenticator, service_instance_id=SERVICE_INSTANCE_ID, service_url=service_credentials["url"])
        return wos_client
    except Exception as e:
        print(f"Error during authentication: {e}")
        return "Watson OpenScale Client Error"



# POST /v2/predict_and_log to make predictions and then store request and response data to payload logging and feedback logging tables
# Note: Feedback logging table requires label data
@app.route("/v2/predict_and_log", methods=["POST"])
def predict_and_log():
    try:
        payload = request.get_json()
        payload_scoring_request={}
        payload_scoring_request['fields']=payload['input_data'][0]['fields'][:-1]
        payload_scoring_request['values']=[i[:-1] for i in payload['input_data'][0]['values']]
        payload_scoring_request['meta']={'fields':['gender_m'], 'values':[[i[8]] for i in payload['input_data'][0]['values']]}
     
        payload_scoring_response = predict(payload)
        predictions=payload_scoring_response

        # Payload Logging
        wos_client = openscale_authentication()
        payload_logging_data_set_id = wos_client.data_sets.list(type=DataSetTypes.PAYLOAD_LOGGING, target_target_id=subscription_id, target_target_type=TargetTypes.SUBSCRIPTION).result.data_sets[0].metadata.id

        wos_client.data_sets.store_records(data_set_id=payload_logging_data_set_id, request_body=[PayloadRecord(request=payload_scoring_request, response=payload_scoring_response, response_time=460)])
        print("payload logging successful")
        print("payload : --",payload_scoring_request)
        print("response: --",payload_scoring_response)

        # Feedback Logging
        feedback_log_req={}
        feedback_log_req['fields']=payload['input_data'][0]['fields']+["_original_prediction","_original_probability","_debiased_prediction","_debiased_probability"]        
        feedback_log_req['values']=[]
        
        for x in range(len(payload_scoring_response['predictions'][0]['values'])):
            feedback_log_req['values'].append(payload['input_data'][0]['values'][x]+predictions['predictions'][0]['values'][x]+predictions['predictions'][0]['values'][x])

        feedback_dataset_id = wos_client.data_sets.list(type=DataSetTypes.FEEDBACK, target_target_id=subscription_id, target_target_type=TargetTypes.SUBSCRIPTION).result.data_sets[0].metadata.id

        print("feedback req: ---",feedback_log_req)
        
        wos_client.data_sets.store_records(
                data_set_id=feedback_dataset_id,
                request_body=[feedback_log_req],
                background_mode=False
        )

        print("feedback logging successful")
        response="Payload Logging and Feedback logging Successful"
    except Exception as e:
        print(f"Error during Logging: {e}")
        response="Logging Failed"

    output={"model_prediction":payload_scoring_response,"logging_response":response}
    
    return jsonify(output)

# POST /v2/feedback_logging to make predictions and then store request and response data to feedback logging table
# Note: Feedback logging table requires label data
@app.route("/v2/feedback_logging", methods=["POST"])
def feedback_logging():
    payload = request.get_json()
    predictions=predict(payload)
    feedback_log_req={}
    feedback_log_req['fields']=payload['input_data'][0]['fields']+["is_promoted"]+["_original_prediction","_original_probability","_debiased_prediction","_debiased_probability"]
    feedback_log_req['values']=[]
    for x in range(len(predictions['predictions'][0]['values'])):
         feedback_log_req['values'].append(payload['input_data'][0]['values'][x]+[int(predictions['predictions'][0]['values'][x][0])]+predictions['predictions'][0]['values'][x]+predictions['predictions'][0]['values'][x])

    try:
        wos_client = openscale_authentication()
        feedback_dataset_id = wos_client.data_sets.list(type=DataSetTypes.FEEDBACK, target_target_id=subscription_id, target_target_type=TargetTypes.SUBSCRIPTION).result.data_sets[0].metadata.id

        wos_client.data_sets.store_records(
                data_set_id=feedback_dataset_id,
                request_body=[feedback_log_req],
                background_mode=False
        )
        return "Feedback Logging Successfull"

    except Exception as e:
        print(f"Error during logging: {e}")
        return "Feedback Logging Failed, Please check your watson openscale instance and verify the inputs"

# POST /v2/payload_logging to make predictions and then store request and response data to payload logging table
@app.route("/v2/payload_logging", methods=["POST"])
def payload_logging():
    try:
        payload = request.get_json()
        payload_scoring_request={}
        payload_scoring_request['fields']=payload['input_data'][0]['fields'][:-1]

        payload_scoring_request['values']=[i[:-1] for i in payload['input_data'][0]['values']]

        payload_scoring_request['meta']={'fields':['referrer_gender'], 'values':[[i[8]] for i in payload['input_data'][0]['values']]}
        payload_scoring_response = predict(payload)

        predictions=payload_scoring_response

        # Payload Logging
        wos_client = openscale_authentication()
        payload_logging_data_set_id = wos_client.data_sets.list(type=DataSetTypes.PAYLOAD_LOGGING, target_target_id=subscription_id, target_target_type=TargetTypes.SUBSCRIPTION).result.data_sets[0].metadata.id

        wos_client.data_sets.store_records(data_set_id=payload_logging_data_set_id, request_body=[PayloadRecord(request=payload_scoring_request, response=payload_scoring_response, response_time=460)])
        return "payload logging successful"
    except Exception as e:
        print(f"Error during logging: {e}")
        return "payload logging Failed, Please check your watson openscale instance and verify the inputs"

if __name__ == "__main__":
    print("Serving Initializing")
    print("Serving Started")
    app.run(host="0.0.0.0", debug=True, port=7000)

