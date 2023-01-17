"""Script to recognize the image files from prior step"""
import argparse
import time
import logging
import os
import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import document_analysis_client
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def get_file_list(pathway):
    """Script to get all image file paths"""
    file_paths = []
    for root, _, filenames in os.walk(pathway):
        for filename in filenames:
            file_paths.append(os.path.join(root, filename))
    return file_paths


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


def main(source=None, output_path=None):
    image_filepaths = get_file_list(source)
    print(f"Image Directories: {image_filepaths}")

    # For each file, create discrete images
    for i, _ in enumerate(image_filepaths):

        # Create the output path for the recognizer output
        image_directory = image_filepaths[i].split('/')[-2:][0]
        image_filename = image_filepaths[i].split('/')[-2:][1]
        image_filename = image_filename.replace('png', 'txt')

        # Create outputPath with the directory
        outputPath = output_path + '/' + str(image_directory)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        result = analyze_read(client=document_analysis_client, image_file=image_filepaths[i])
        # logging.info(f"Content for {image_filenames[i]}: {result}")
        write_out_output(result=result, output_path=outputPath, filename=image_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_data", help="Input files to process")
    parser.add_argument("-o", "--output_data", help="Output files to process")
    args = parser.parse_args()

    main(source=args.input_data, output_path=args.output_data)
