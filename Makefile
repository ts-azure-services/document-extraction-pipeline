venv-setup:
	rm -rf .venv
	python3.11 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r ./requirements.txt

sub-init:
	echo "SUB_ID=<enter subscription name>" > sub.env

# This not only sets up infra but converts the blob stores -> ADLS Gen 2
infra:
	./setup/create-resources.sh

create-cluster:
	.venv/bin/python ./common/cluster.py

create-env:
	.venv/bin/python ./common/env.py --name "pdf-split-env" --conda_file "./config/pdf-env.yml"
	.venv/bin/python ./common/env.py --name "form-rec-env" --conda_file "./config/form-rec-env.yml"
	.venv/bin/python ./common/env.py --name "parallel-env" --conda_file "./config/parallel-env.yml"

pdf_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_PDF" | cut -d "=" -f 2 | xargs)
image_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_IMAGES" | cut -d "=" -f 2 | xargs)
text_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_TXT" | cut -d "=" -f 2 | xargs)
create-datastores:
	.venv/bin/python ./common/datastore.py --container_name $(pdf_blob) \
		--datastore_name "pdfinputfiles" \
		--datastore_desc "PDF input files"
	.venv/bin/python ./common/datastore.py --container_name $(image_blob) \
		--datastore_name "pdfimages" \
		--datastore_desc "PDF image files"
	.venv/bin/python ./common/datastore.py --container_name $(text_blob) \
		--datastore_name "textfiles" \
		--datastore_desc "Final text files"

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


## Single step experiment
primary_datastore="azureml://datastores/pdfinputfiles/paths/"
intermediate_datastore="azureml://datastores/pdfimages/paths/"
output_datastore="azureml://datastores/textfiles/paths/"
single-job:
	.venv/bin/python ./single-step-job/main.py --input_datastore $(primary_datastore) \
		--output_datastore $(intermediate_datastore)

# Sequential pipeline: PDF -> images, and then form recognizer on those images
seq-pipeline:
	.venv/bin/python ./pipeline-sequential/main.py \
		--input_datastore $(primary_datastore) \
		--intermediate_datastore $(intermediate_datastore) \
		--output_datastore $(output_datastore)

# Similar to sequential process, but in parallel
# Note that before running this, you should insert the Form Recognizer key into the second component
par-pipeline:
	.venv/bin/python ./pipeline-parallel/main.py \
		--input_datastore $(primary_datastore) \
		--intermediate_datastore $(intermediate_datastore) \
		--output_datastore $(output_datastore)

# Commit local branch changes
branch=$(shell git symbolic-ref --short HEAD)
now=$(shell date '+%F_%H:%M:%S' )
git-push:
	git add . && git commit -m "Changes as of $(now)" && git push -u origin $(branch)

git-pull:
	git pull origin $(branch)python ./pipeline-parallel/main.py
