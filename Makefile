# For local dev environment
install:
	#conda create -n doc-pipeline python=3.8 -y; conda activate doc-pipeline
	pip install python-dotenv
	pip install azure-ai-ml
	pip install azure-identity
	pip install pandas
	pip install flake8
	pip install azure-ai-formrecognizer

infra:
	./setup/create-resources.sh

create_cluster:
	python ./common/cluster.py

create_env:
	python ./common/env.py --name "pdf-split-env" --conda_file "./config/pdf-env.yml"
	python ./common/env.py --name "form-rec-env" --conda_file "./config/form-rec-env.yml"
	python ./common/env.py --name "parallel-env" --conda_file "./config/parallel-env.yml"

# Change default blob store to an ADLS by changing 'Hierarchial namespace'. Ensure above operation completes.
# Upload sample pdf files from /data/ to folder `pdf-inputs`, under the default blob store

## Single step experiment
single_job:
	python ./single-step-job/main.py

# Sequential pipeline: PDF -> images, and then form recognizer on those images
seq_pipeline:
	python ./pipeline-sequential/main.py

par_pipeline:
	python ./pipeline-parallel/main.py
