"""Script to create images from PDF files"""
import os
import argparse
from pdf2image import convert_from_path


def get_file_list(pathway):
    """Script to get all image file paths"""
    file_paths = []
    for root, _, filenames in os.walk(pathway):
        for filename in filenames:
            if ".pdf" in filename:
                file_paths.append(os.path.join(root, filename))
    return file_paths


def main(source=None, output_path=None):
    pdf_list = get_file_list(source)
    print(f"Number of PDFs: {len(pdf_list)}")
    print(f"PDF List: {pdf_list}")

    # For each file, create discrete images
    for i, _ in enumerate(pdf_list):

        # Create the output path for the PDF output
        pdf_directory = pdf_list[i].split('/')[-1:][0]
        pdf_directory = pdf_directory.replace('.pdf', '')

        # Create the output path first
        outputPath = output_path + '/' + str(pdf_directory)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        images = convert_from_path(pdf_list[i])
        print(f'For {pdf_list[i]}, have created {len(images)} images')
        for j, _ in enumerate(images):
            images[j].save(outputPath + "/" + "page" + str(j) + '.png')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_data", help="Input files to process")
    parser.add_argument("-o", "--output_data", help="Output files to process")
    args = parser.parse_args()

    # Start execution, and time
    main(source=args.input_data, output_path=args.output_data)
