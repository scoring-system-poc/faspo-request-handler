import asyncio
import typing
import datetime as dt
import azure.cosmos.aio
import azure.identity.aio

from src.core.config import CONFIG


client = azure.cosmos.aio.CosmosClient(
    url=CONFIG.COSMOS_URL,
    credential=azure.identity.aio.WorkloadIdentityCredential(
        tenant_id=CONFIG.AZURE_TENANT_ID,
        client_id=CONFIG.AZURE_CLIENT_ID,
        token_file_path=CONFIG.AZURE_FEDERATED_TOKEN_FILE,
    ),
)

db = client.get_database_client(
    database=CONFIG.COSMOS_DB,
)

c_document = db.get_container_client(
    container=CONFIG.COSMOS_DOCUMENT_CONTAINER,
)

c_subject = db.get_container_client(
    container=CONFIG.COSMOS_SUBJECT_CONTAINER,
)

