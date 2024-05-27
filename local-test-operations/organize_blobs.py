# Script to sort and organize discrete text files into a single text file
import os
import re
import logging
from collections import defaultdict
from pprint import pprint as pp
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


def get_txt_file_hierarchy(blob_service_client: BlobServiceClient, container_name: str):
    container_client = blob_service_client.get_container_client(container=container_name)

    # Upload the new blob from a local file
    blobs_list = container_client.list_blobs()
    directory_list, file_list = [], []

    logging.info(f"Blob list: {blobs_list}")
    for blob in blobs_list:
        logging.info(blob.name)

        if "/" in str(blob.name):
            # File structure
            file_list.append(blob.name)
        else:
            # Folder structure
            directory_list.append(blob.name)

    def sort_key(filename):
        # Split the filename into category and number
        parts = filename.split('/')
        category = parts[0] if len(parts) > 1 else ''
        match = re.search(r'(?P<number>\d+)', parts[-1])
        number = int(match.group('number')) if match else 0
        return (category, number)

    # Organize folder structures to order by page number
    file_list.sort(key=sort_key)

    # Create dictionary of filename and value
    d = defaultdict(list)
    for i in file_list:
        key, _ = i.split('/', 1)
        d[key].append(i)
    result = dict(d)
    return result


def consolidate_text_files(blob_service_client: BlobServiceClient, 
                           container_name: str, 
                           final_container_name: str, 
                           mapping,
                           ):
    # Get each filename in order, retrieve contents and then upload to blob
    for key in mapping:
        logging.info(f"Key: {key}")
        final_text = ""
        for value in mapping[key]:
            print("Value:", value)
            temp_blob_client = blob_service_client.get_blob_client(container_name, value)
            temp_data = temp_blob_client.download_blob().readall()
            final_text = final_text + temp_data.decode('utf-8')# + '/n'

        # Upload the final text into a new blob container
        blob_name = str(key) + '.txt'
        container_output = blob_service_client.get_container_client(container=final_container_name)
        container_output.upload_blob(name=blob_name, data=final_text, overwrite=True)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    load_dotenv('./variables.env')
    connection_string = os.environ["STORAGE_CONN_STRING"]
    container_name = os.environ["BLOB_CONTAINER_TXT"]
    final_container_name = os.environ["BLOB_CONTAINER_TXT_FINAL"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get the mapping of all files and their hierarchy
    mapping = get_txt_file_hierarchy(blob_service_client, container_name)
    logging.info(pp(mapping))

    consolidate_text_files(blob_service_client, 
                           container_name=container_name,
                           final_container_name=final_container_name,
                           mapping=mapping
                           )

