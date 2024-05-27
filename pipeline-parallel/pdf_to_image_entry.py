# Script to create images from PDF files
import os
import logging
import argparse
from pypdf import PdfReader, PdfWriter


def init():
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_output_path", type=str, default=0)
    args, _ = parser.parse_known_args()
    OUTPUT_PATH = args.job_output_path
    logging.info("Pass through init done.")


def run(mini_batch):
    # mini_batch is a list of file paths for File Data
    for file_path in mini_batch:
        logging.info(f'Processing: {file_path}')
        pdf_to_image(file_path)
    return mini_batch


def pdf_to_image(file_path):
    # Get filename and directory name
    file_name = file_path.split('/')[-1:][0]
    file_dir = file_name.replace('.pdf', '')

    # Create the output path first
    outputPath = OUTPUT_PATH + '/' + str(file_dir) + '/'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    # Create the pypdf objects
    reader = PdfReader(open(file_path, 'rb'))
    num_of_pages = len(reader.pages)

    counter = 0
    for page_number in range(num_of_pages):
        writer = PdfWriter()
        page = reader.pages[page_number]
        writer.add_page(page)
        counter += 1
        with open(outputPath + str(page_number) + '.pdf', 'wb') as output:
            writer.write(output)

    logging.info(f"Wrote {counter} pages for {num_of_pages}.")
