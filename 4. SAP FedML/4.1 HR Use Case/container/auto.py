import joblib
import pandas as pd
import json
from flask import Flask, jsonify, request

# Create an instance of the Flask class
app = Flask(__name__)

# Load the machine learning model
model = joblib.load("scikit_model.pkl")

# This function would read and process input data, make predictions, and return a json output.
def predict(payload):
    global model
    payload = payload['input_data'][0]
    df = pd.DataFrame(payload['values'], columns=payload['fields'])
    # Remove the column if it exists
    if 'is_promoted' in df.columns:
        df = df.drop(columns=['is_promoted'])
    try:
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

# Define a route for the root path "/"
# This function will be called when the root URL is accessed.
@app.route("/", methods=["GET"])
def default():
    message = "REST API endpoints for making employee promotion predictions\n" + \
              "  - GET /v2/greet to check if a model is loaded.\n" + \
              "  - POST /v2/predict with your payload to make predictions.\n"
    return message

# Define another route for "/v2/status"
# This function returns the status of the machine learning model
@app.route("/v2/status", methods=["GET"])
def status():
    global model
    if model is None:
        return "Status: Model is not loaded."
    else:
        return "Status: Model is loaded."

# Define a dynamic route for "/v2/predict"
# This function would make predictions and return a json output.
@app.route("/v2/predict", methods=["POST"])
def predict_employee_promotion_response():
    payload = request.get_json()
    try:    
        output = predict(payload)
    except Exception as e:
        print(f"Error during prediction: {e}")
        output = {"ERROR": "Prediction Failed"}
    return jsonify(output)

# The main driver function.
# If this file is executed as the main program, run the application.
if __name__ == "__main__":
    print("Serving Initializing")
    print("Serving Started")
    # Run the Flask application on port 7000.
    app.run(host="0.0.0.0", port=7000)

