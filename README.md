# Integrating watsonx with SAP AI Core and Datasphere

## Introduction
This repo demonstrates different ways watsonx.ai, watsonx.data, and watsonx.governance can be used with SAP's AI Core and Datasphere for AI model training, deployment, and governance monitoring. 

The [SAP AI Core](https://help.sap.com/docs/sap-ai-core) service in the [SAP Business Technology Platform (BTP)](https://help.sap.com/docs/btp) handles the execution and operations of your AI assets in a standardized, scalable, and hyperscaler-agnostic way.

[SAP Datasphere](https://help.sap.com/docs/SAP_DATASPHERE) provides a business data fabric infrastructure that can work across an organization to bring together mission-critical data. SAP Datasphere allows you to converge data coming from SAP and third-party on-premise and cloud environments into a single, fully-managed cloud environment.
 
## watsonx with SAP AI Core
watsonx provides powerful tools that can be used each step of an AI model's lifecycle.

This architecture diagram will be used in our lifecycle discussion.

![End to End flow](./images/end-to-end-flow.png)

### Data Ingestion
Gathering model training data often requires retrieving and joining data from multiple data sources. While this can be done directly in a notebook, this approach may not scale for large datasets or when data security limits data visibility. The watsonx.data tutorial explores ways to retrieve and join data from multiple databases using watsonx.data.

Path #1 - connecting SAP Datasphere to watsonx.data. This is not yet working, but we are investigating using SAP's custom JDBC driver with watsonx.data.

Path #2 and #3 - connecting multiple databases (DB2 and Netezza in the diagram) and using a federated query to join data (path #4) from multiple tables.

### Data Exploration
The watsonx.ai Studio provides Jupyter notebook environments that can be used for data exploration. Studio also provides a visualization environment with a large selection of graph types to explore all aspects of your data.

### Model Training
Models can be trained in a Jupyter notebook running in Watson Studio, which provides a secure environment for sensitive data. Training data could be retrieved from watsonx.data (path #6) or pulled directly from a database (path #5 shows direct data retrieval from SAP Datasphere). The model is created, fine-tuned, and evaluated in this environment.

### Model Deployment
Once trained, the model can be deployed to SAP AI Core (path #7) where it can be invoked for inferencing.

### Model Governance
watsonx.governance enables you to track the prominence of data used to train a model (this is done in IBM OpenPages) and to monitor the health and model performance over time (this is done in IBM OpenScale). OpenScale gives the ability to monitor a model for ongoing fairness, quality, and explainability.

Configuring a model for OpenScale monitoring requires:
1. Configuring OpenScale to receive monitoring data from the model (path #7).
2. Configuring the fairness, quality, and explainability settings for the model (path #8).

After the model has been configured for monitoring, invoking the model causes it to return metrics to OpenScale (path #9).

### Model in Production
With the model and governance in place, it can now be invoked by an application to score data (path #10).


Prior to model training a data scientists wants to explore the data to get a feel for relationships between 

## Examples
The end-to-end lifecycles has been broken into smaller examples that focus on one of the watsonx products.

### watsonx.ai
This example demonstrates [IBM watsonx](https://www.ibm.com/watsonx) retrieving training data from SAP Datasphere, training a model in Watson Studio, and then deploying the model to SAP AI Core.

The model trained in this example is a Watson NLP text classification model that predicts the recommended emergency handling protocols for different types of hazards materials based on information found in the bill of lading. Details on the use case can be found [here](./docs/watsonx-ai.md)

Two Jupyter Notebooks are provided to demonstrate the complete end-to-end flow:

1. [Train a classification model for MSDS in IBM Watson Studio](notebooks/Train-Model-with-Data-from-SAP-Datasphere.ipynb)
1. [Deploy the custom-trained model to SAP AI Core](notebooks/Deploy-Custom-Model-to-SAP-AI-Core.ipynb)

### watsonx.data

(./docs/watsonx-data-integration.md)



### watsonx.governance

(./docs/watsonx-data-governance.md)