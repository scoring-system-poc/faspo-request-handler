# [ FASPO ] Request Handler

This repository contains source code for the _Request Handler_ in FASPO concept project. The _Request Handler_ is 
a part of much larger system that is utilizing microservices architecture. It's main responsibility is to pretty much
be a brain of backend for FASPO system. It exposes API for external apps and delegates work to other microservices.


## Prerequisites

* Python 3.11 or higher
* packages listed in `requirements.txt`
* Docker (optional, for containerization)

## Environment Variables

* `APPLICATIONINSIGHTS_CONNECTION_STRING`
  * Connection string for Azure Application Insights
  * for local testing set to `InstrumentationKey=00000000-0000-0000-0000-000000000000` and ignore errors from `azure.monitor.opentelemetry`
* `AZURE_CLIENT_ID`
  * Client ID for related UAMI
* `AZURE_TENANT_ID`
  * Tenant ID where the UAMI is located
* `AZURE_FEDERATED_TOKEN_FILE`
  * Location of the Azure federated token file
  * default: `/var/run/secrets/azure/tokens/azure-identity-token`
* `COSMOS_URL`
  * URL for the Azure Cosmos DB
* `COSMOS_DB`
  * Database name for the Azure Cosmos DB
* `COSMOS_SUBJECT_CONTAINER`
  * Container name for the subject data
  * default: `subject`
* `COSMOS_DOCUMENT_CONTAINER`
  * `Container name for the document data
  * default: `document`
* `ONLINE_DATA_SERVICE_URL`
  * URL of the internal data target, i.e. Online-Data Service HOST
* `MODEL_SERVICE_URL`
  * URL of the internal data target, i.e. Model Service HOST
* `EXPORT_SERVICE_URL`
  * URL of the internal data target, i.e. Export Service HOST
* `LOG_INFO`: 
  * Log level for info messages 
  * default: `INFO`

## Installation (Direct)

1. Make sure Python 3.11 is installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the project directory.
4. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   ```
5. Activate the virtual environment:
    ```bash
     source venv/bin/activate
     ```
6. Install the required packages:
7. ```bash
   pip install -r requirements.txt
   ```
9. Run the application:
   ```bash
   python main.py
   ```
   or
   ```bash
   uvicorn main:app --host <your_host> --port <your_port>
   ```
10. The application should now be running and accessible at `http://0.0.0.0:8080`.

## Installation (Docker)

1. Make sure Docker is installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the project directory.
4. Build the Docker image:
   ```bash
   docker build -t request-handler .
   ```
5. Run the Docker container:
   ```bash
    docker run -d -p 8080:8080 --env <ENV_NAME>=<ENV_VALUE> -- request-handler
    ```
