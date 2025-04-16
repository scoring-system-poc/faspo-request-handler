import pytest


@pytest.mark.asyncio
async def test_config(mock_environ) -> None:
    from src.core.config import CONFIG

    assert CONFIG.AZURE_CLIENT_ID == "00000000-0000-0000-0000-000000000000"
    assert CONFIG.AZURE_TENANT_ID == "00000000-0000-0000-0000-000000000000"
    assert CONFIG.AZURE_FEDERATED_TOKEN_FILE == "/var/run/secrets/azure/tokens/azure-identity-token"
    assert CONFIG.COSMOS_URL == "https://test.documents.azure.com:443/"
    assert CONFIG.COSMOS_DB == "test"
    assert CONFIG.COSMOS_DOCUMENT_CONTAINER == "document"
    assert CONFIG.COSMOS_SUBJECT_CONTAINER == "subject"
    assert CONFIG.ONLINE_DATA_SERVICE_URL == "http://faspo-online-data-service/api/v1"
    assert CONFIG.MODEL_SERVICE_URL == "http://faspo-model-service/api/v1"
    assert CONFIG.EXPORT_SERVICE_URL == "http://faspo-export-service/api/v1"
    assert CONFIG.LOG_LEVEL == "INFO"

