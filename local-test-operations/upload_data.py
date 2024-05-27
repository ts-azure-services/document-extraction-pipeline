import os
import time
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


# def delete_blob_files(blob_service_client: BlobServiceClient, container_name: str):
#     """Delete existing files"""
#     # Get the container client
#     container_client = blob_service_client.get_container_client(container=container_name)
#
#     # First delete individual files recursively
#     for blob in container_client.list_blobs():
#         if ".pdf" in blob.name or ".txt" in blob.name:
#             container_client.delete_blob(blob.name)
#
#     time.sleep(2)
#
#     # Once folders have no files, then you can delete folders
#     # However, folders within folders are classified as non-empty
#     # So first list out all folder structures, and from the lowest level down, delete them
#     folder_lists = []
#     for blob in container_client.list_blobs():
#         folder_lists.append(blob.name)
#
#     # Delete in reverse
#     folder_lists.reverse()
#     for blob in folder_lists:
#         container_client.delete_blob(blob)
#         time.sleep(0.5)

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
    logging.basicConfig(level=logging.DEBUG)
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
