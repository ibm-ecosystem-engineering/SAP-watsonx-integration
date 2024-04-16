# README

## Build the Docker image
Save the pickle file of the trained model as `scikit_model.pkl`, and run the following command to build a runtime container image for serving the model on Docker, SAP AI Core, and other cloud container environments.

```
docker compose build
```

## Start the runtime container on Docker

You can start the runtime container locally on Docker for test & development purposes.

```
docker compose up
```

## Test it using curl commands

You can run some simple tests aginst the REST APIs using curl commands.

Make a REST call to the root path "/" of the endpoint, which should list a couple of APIs:

```
$ curl -X GET http://127.0.0.1:7000
REST API endpoints for making employee promotion predictions
  - GET /v2/greet to check if a model is loaded.
  - POST /v2/predict with your payload to make predictions.
```

Use the `GET /v2/status` API to get the status of the machine learning model:

```
$ curl -X GET http://127.0.0.1:7000/v2/status
Status: Model is loaded.
```

Use the `POST /v2/predict` API to make an inference call:

```
$ curl -X POST -H 'Content-type: application/json' http://127.0.0.1:7000/v2/predict -d @test.json
{"predictions":[{"fields":["prediction","probability"],"values":[[0,[0.95,0.05]]]}]}
```

## Push the Docker image to container registry

If your local tests pass, you can push the Docker image to your container registry for deployment on other environments. For example:

```
docker image tag epp-local-test:latest <dockerhub_username>/<repository>:<tag>
docker image push <dockerhub_username>/<repository>:<tag>
```

