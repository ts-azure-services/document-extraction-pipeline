# Script to delete blobs, including folders with non-empty values
import os
import time
import logging
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def delete_blob_files(blob_service_client: BlobServiceClient, container_name: str):
    """Delete existing files"""
    container_client = blob_service_client.get_container_client(container=container_name)

    # First delete individual files recursively
    for blob in container_client.list_blobs():
        if ".pdf" in blob.name or ".txt" in blob.name:
            container_client.delete_blob(blob.name)

    time.sleep(2)

    # Once folders have no files, you can delete folders
    # However, folders within folders are classified as non-empty
    # So first list out all folder structures, and from the lowest level down, delete them
    folder_lists = []
    for blob in container_client.list_blobs():
        folder_lists.append(blob.name)

    # Delete in reverse
    folder_lists.reverse()
    for blob in folder_lists:
        container_client.delete_blob(blob)
        time.sleep(0.5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    load_dotenv('./variables.env')
    connection_string = os.environ["STORAGE_CONN_STRING"]

    # Container to delete
    container_name = os.environ["BLOB_CONTAINER_IMAGES"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Delete existing blobs
    delete_blob_files(blob_service_client, container_name)
    logging.info("Deleted existing files...")
