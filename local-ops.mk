# This is a sub Makefile to capture make operations for discrete scripts

# For a sample PDF, refer the azure-ai-studio documentation; this should be a +700 page pdf
## If running in the cloud shell, upload the azure-ai-studio pdf
# Then, use the script below to generate several PDFs out of this base PDF and upload to blob
input_file="./azure-ai-studio.pdf"
number_of_pdfs=10
create-pdfs:
	rm -rf ./data
	mkdir -p ./data
	.venv/bin/python ./local-test-operations/create_pdfs.py --input_file=$(input_file) --number_of_pdfs=$(number_of_pdfs)


# Upload files to blob container = pdf-files
# Note that if there is a folder structure inherent in the data folder ahead of time, it will just upload discrete files
upload-files:
	.venv/bin/python ./local-test-operations/upload_data.py



# Delete all blobs in a specific container
# Container hard-coded into the script
delete-container:
	.venv/bin/python ./local-test-operations/delete_blobs.py


# When you have discrete text files and need to consolidate them into a new file
# Source and destination container hard-coded into the script
consolidate-text-files:
	.venv/bin/python ./local-test-operations/organize_blobs.py
