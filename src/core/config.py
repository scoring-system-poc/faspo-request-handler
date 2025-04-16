import pydantic
import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    """
    Environment configuration for the application.
    """
    # Azure
    AZURE_CLIENT_ID: str
    AZURE_TENANT_ID: str
    AZURE_FEDERATED_TOKEN_FILE: str = "/var/run/secrets/azure/tokens/azure-identity-token"

    # CosmosDB
    COSMOS_URL: str
    COSMOS_DB: str

    COSMOS_SUBJECT_CONTAINER: str = "subject"
    COSMOS_DOCUMENT_CONTAINER: str = "document"

    # Microservices
    ONLINE_DATA_SERVICE_URL: str = "http://faspo-online-data-service/api/v1"
    MODEL_SERVICE_URL: str = "http://faspo-model-service/api/v1"
    EXPORT_SERVICE_URL: str = "http://faspo-export-service/api/v1"
    STORE_SERVICE_URL: str = "http://faspo-store-service/api/v1"    # this is only temporary (for subject creation)

    # General
    LOG_LEVEL: pydantic.constr(to_upper=True) = "INFO"


CONFIG = Config()
