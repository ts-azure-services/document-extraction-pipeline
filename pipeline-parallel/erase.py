# Script to delete blobs, including folders with non-empty values
import os
import argparse
import time
import logging
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

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

    parser = argparse.ArgumentParser()
    # parser.add_argument("--storage_connection", help="Storage connection")
    parser.add_argument("--page_pdf_container", help="Container with page-level PDFs")
    parser.add_argument("--page_txt_container", help="Container with page-level text files")
    parser.add_argument("--final_txt_container", help="Container with final text file outputs")
    parser.add_argument("--job_output_path", help="Output Azure ML datastore to connect to next pipeline step")
    args = parser.parse_args()

    blob_service_client = BlobServiceClient.from_connection_string(os.environ['STORAGE_CONN_STRING'])

    # Delete page pdf container
    delete_blob_files(blob_service_client,args.page_pdf_container)
    logging.info(f"Deleted all files in {args.page_pdf_container}...")
    
    # Delete page_txt_container
    delete_blob_files(blob_service_client, args.page_txt_container)
    logging.info(f"Deleted all files in {args.page_txt_container}...")

    # Delete final_txt_connector
    delete_blob_files(blob_service_client, args.final_txt_container)
    logging.info(f"Deleted all files in {args.final_txt_container}...")
