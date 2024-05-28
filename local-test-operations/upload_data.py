import os
import logging
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from delete_blobs import delete_blob_files

def get_data_files(start_path="./data"):
    """Get all generated data files"""
    filepath_list = []
    for root, _ , files in os.walk(start_path):
        for file in files:
            filepath_list.append(os.path.join(root, file))
    return filepath_list


def upload_blob_file(blob_service_client: BlobServiceClient, container_name: str, local_file_path: str):
    """Upload blob files"""
    # Get the container client
    container_client = blob_service_client.get_container_client(container=container_name)

    # Upload the new blob from a local file
    blob_name = local_file_path.split('/')[-1]
    with open(file=local_file_path, mode="rb") as data:
        # blob_client = container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv('./variables.env')
    connection_string = os.environ["STORAGE_CONN_STRING"]
    container_name = os.environ["BLOB_CONTAINER_PDF"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Delete existing blobs
    delete_blob_files(blob_service_client, container_name)
    logging.info("Deleted existing files...")

    # Upload new files
    data_file_list = get_data_files()

    for file in data_file_list:
        upload_blob_file(blob_service_client, container_name, file)
        logging.info(f"Uploaded file: {file}")
