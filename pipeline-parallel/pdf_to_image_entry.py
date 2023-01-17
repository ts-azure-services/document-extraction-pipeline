"""Script to create images from PDF files"""
import os
import argparse
from pdf2image import convert_from_path
from pathlib import Path


def init():
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_output_path", type=str, default=0)
    args, _ = parser.parse_known_args()
    OUTPUT_PATH = args.job_output_path
    print("Pass through init done.")


def run(mini_batch):
    # mini_batch is a list of file paths for File Data
    for file_path in mini_batch:
        print(f'Processing: {file_path}')
        pdf_to_image(file_path)
    return mini_batch


def pdf_to_image(file_path):
    # Get filename and directory name
    file_name = file_path.split('/')[-1:][0]
    file_dir = file_name.replace('.pdf', '')
    images = convert_from_path(file_path)
    print(f'For {file_name}, have generated {len(images)} images')
    # Create the output path first
    outputPath = OUTPUT_PATH + '/' + str(file_dir) + '/'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    # Save images to outputpath
    for j, _ in enumerate(images):
        images[j].save(outputPath + "page" + str(j) + '.png')
