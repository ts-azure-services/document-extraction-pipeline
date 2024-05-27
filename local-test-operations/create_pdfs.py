import argparse
import random
import uuid
import logging
from pypdf import PdfReader, PdfWriter

def create_random_pdf(input_pdf, num_of_pdfs):
    """Create new PDFs based upon page count and number"""
    reader = PdfReader(open(input_pdf, 'rb'))

    for _ in range(num_of_pdfs):
        writer = PdfWriter()
        filename = f"{uuid.uuid4()}.pdf"
        num_pages = random.randint(1,5)
        for _ in range(num_pages):
            page_number = random.randint(0, len(reader.pages) - 1)
            page = reader.pages[page_number]
            writer.add_page(page)

        with open('./data/' + filename, 'wb') as output:
            writer.write(output)
        logging.info(f"Wrote out {filename} with {num_pages} pages.")

def main(input, number_of_pdfs):
    create_random_pdf(input, number_of_pdfs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Create PDFs')
    parser.add_argument('--input_file', type=str, required=True, help='The input file')
    parser.add_argument('--number_of_pdfs', type=str, required=True, help='The number of files to create')
    args = parser.parse_args()

    main(args.input_file, int(args.number_of_pdfs))
