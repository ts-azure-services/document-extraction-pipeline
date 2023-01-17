from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml import command, MLClient, dsl, Input, Output
from azure.identity import DefaultAzureCredential
from azure.ai.ml.parallel import parallel_run_function, RunFunction
import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import ml_client

# Paths for output to be persisted
blob_store_path="azureml://datastores/workspaceblobstore/paths/parallel-pipeline-pdf-images/"
ocr_store_path="azureml://datastores/workspaceblobstore/paths/parallel-pipeline-ocr-outputs/"

# Process PDFs
pdf_parallel_component = parallel_run_function(
    name="process-pdfs",
    display_name="Process PDFs into images",
    description="parallel component for PDF processing",
    inputs=dict(job_data_path=Input(type=AssetTypes.URI_FOLDER,)),
    input_data="${{inputs.job_data_path}}",
    outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER, path=blob_store_path)),
    instance_count=4,
    max_concurrency_per_instance=2,
    mini_batch_size="1",
    mini_batch_error_threshold=1,
    retry_settings=dict(max_retries=2, timeout=60),
    logging_level="DEBUG",
    task=RunFunction(
        code="./",
        entry_script="./pipeline-parallel/pdf_to_image_entry.py",
        program_arguments="--job_output_path ${{outputs.job_output_path}}",
        environment="parallel-env:2",
    ),
)

# Convert images to OCR
ocr_convert_component = parallel_run_function(
    name="convert-images-to-ocr",
    display_name="Convert images to OCR",
    description="Convert images to OCR using Form Recognizer",
    inputs=dict(job_data_path=Input(type=AssetTypes.URI_FOLDER,)),
    input_data="${{inputs.job_data_path}}",
    outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER)),# path=blob_store_path)),
    instance_count=4,
    max_concurrency_per_instance=2,
    mini_batch_size="1",
    mini_batch_error_threshold=1,
    retry_settings=dict(max_retries=2, timeout=60),
    logging_level="DEBUG",
    task=RunFunction(
        code="./",
        entry_script="./pipeline-parallel/png_to_ocr_entry.py",
        program_arguments="--job_output_path ${{outputs.job_output_path}}",
        environment="form-rec-env:2",
    ),
)

# DEFINE THE PIPELINE
@dsl.pipeline(compute='cpu-cluster',)
def par_pipeline(pdf_inputs):
    # using data_prep_function like a python call with its own inputs
    process_pdfs = pdf_parallel_component(job_data_path=pdf_inputs)

    # Solution 1; remove the line below, to let the setting for blob_store_path defined above persist
    # return {"pipeline_job_output":process_pdfs.outputs.job_output_path}

    ocr_conversion = ocr_convert_component(job_data_path=process_pdfs.outputs.job_output_path)

    # Solution 2; return the process_pdfs, but after instantiation, set path to blob_store_path
    return {"pdf_job_output": process_pdfs.outputs.job_output_path,
            "ocr_job_output": ocr_conversion.outputs.job_output_path
            }

# INSTANTIATE THE PIPELINE
pipeline = par_pipeline(pdf_inputs=Input(type=AssetTypes.URI_FOLDER, path="azureml://datastores/workspaceblobstore/paths/pdf-files/"),)
pipeline.outputs.pdf_job_output = Output(type=AssetTypes.URI_FOLDER, path=blob_store_path)
pipeline.outputs.ocr_job_output = Output(type=AssetTypes.URI_FOLDER, path=ocr_store_path)

# SUBMIT THE PIPELINE JOB
pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="pipeline-parallel",)
