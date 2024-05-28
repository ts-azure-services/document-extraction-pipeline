# Script to provide the authentication object
import os
from azure.ai.ml import MLClient
from azure.identity import EnvironmentCredential # DefaultAzureCredential
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

def load_variables():
    """Load authentication details"""
    env_var = load_dotenv('./variables.env')
    auth_dict = {
            "subscription_id": os.environ['SUB_ID'],
            "resource_group": os.environ['RESOURCE_GROUP'],
            "workspace": os.environ['WORKSPACE_NAME'],
            "client_id": os.environ['AZURE_CLIENT_ID'], #hardcoded with EnvironmentCredential
            "tenant_id": os.environ['AZURE_TENANT_ID'], #hardcoded with EnvironmentCredential
            "client_secret": os.environ['AZURE_CLIENT_SECRET'], #hardcoded with EnvironmentCredential
            "resource": os.environ['COG_RESOURCE'],
            "storage_account": os.environ['STORAGE_ACCOUNT'],
            "storage_connection_key": os.environ['STORAGE_CONN_STRING'],
            "storage_account_key": os.environ['STORAGE_ACCOUNT_KEY'],
            "key": os.environ['COG_KEY'],
            "blob_container_pdf":os.environ['BLOB_CONTAINER_PDF'],
            "blob_container_images":os.environ['BLOB_CONTAINER_IMAGES'],
            "blob_container_txt":os.environ['BLOB_CONTAINER_TXT'],
            "blob_container_final":os.environ['BLOB_CONTAINER_FINAL'],
            "endpoint": os.environ['ENDPOINT'],
            "location": os.environ['LOCATION'],
            }
    return auth_dict


auth_var = load_variables()


ml_client = MLClient(credential=EnvironmentCredential(),
                     subscription_id=auth_var['subscription_id'],
                     resource_group_name=auth_var['resource_group'],
                     workspace_name=auth_var['workspace'],)


document_analysis_client = DocumentAnalysisClient(
        endpoint=auth_var['endpoint'],
        credential=AzureKeyCredential(auth_var['key']),
)
