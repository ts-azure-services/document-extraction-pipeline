"""Script to create images from PDF files"""
import os
import argparse
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# from common.authenticate import document_analysis_client


def init():
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_output_path", type=str, default=0)
    args, _ = parser.parse_known_args()
    OUTPUT_PATH = args.job_output_path

    # # Declare document_analysis_client globally
    # load_dotenv('./../variables.env')
    # auth_dict = {
    #         "key": os.environ['COG_KEY'],
    #         "endpoint": os.environ['ENDPOINT'],
    #         }
    #
    global document_analysis_client
    # document_analysis_client = DocumentAnalysisClient(
    #         endpoint=auth_dict['endpoint'],
    #         credential=AzureKeyCredential(auth_dict['key']),
    # )
    document_analysis_client = DocumentAnalysisClient(
            endpoint='https://westus.api.cognitive.microsoft.com/',
            credential=AzureKeyCredential('<enter the api key>'),
    )
    print("Pass through init done.")


def run(mini_batch):
    # mini_batch is a list of file paths for File Data
    for file_path in mini_batch:
        print(f'Processing: {file_path}')
        get_ocr_from_image(file_path)
    return mini_batch


# Get form recognizer output
def analyze_read(client=None, image_file=None):
    """Get form recognizer analysis"""
    with open(image_file, 'rb') as filename:
        poller = client.begin_analyze_document("prebuilt-read", document=filename, locale='en-US')
    result = poller.result()
    return result.content


# Write out and save results to a file
def write_out_output(result=None, output_path=None, filename=None):
    with open(output_path + '/' + filename, 'w') as f:
        f.write(result)


def get_ocr_from_image(file_path):
    # Create the output path for the recognizer output
    image_directory = file_path.split('/')[-2:][0]
    image_filename = file_path.split('/')[-2:][1]
    image_filename = image_filename.replace('png', 'txt')

    # Create outputPath with the directory
    outputPath = OUTPUT_PATH + '/' + str(image_directory)
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    result = analyze_read(client=document_analysis_client, image_file=file_path)
    # logging.info(f"Content for {image_filenames[i]}: {result}")
    write_out_output(result=result, output_path=outputPath, filename=image_filename)
