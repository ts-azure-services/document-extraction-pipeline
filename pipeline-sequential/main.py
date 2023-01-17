# from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import command, dsl, Input, Output
# from azure.identity import DefaultAzureCredential
import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import ml_client


# Define paths for specific outputs
blob_store_path="azureml://datastores/workspaceblobstore/paths/seq-pipeline-pdf-images/"
ocr_store_path="azureml://datastores/workspaceblobstore/paths/seq-pipeline-ocr-outputs/"

# Defining pipeline components
data_split_component = command(
    code="./",
    inputs={"input_data": Input(type=AssetTypes.URI_FOLDER)},
    outputs={"output_data": Output(type=AssetTypes.URI_FOLDER, path=blob_store_path)},
    command="python ./pipeline-sequential/pdf_to_png.py --input_data ${{inputs.input_data}} --output_data ${{outputs.output_data}}",
    environment="pdf-split-env:1",
    compute="cpu-cluster",
)


# Second component is to just print out the list of files
form_recognizer_component = command(
    code="./",
    inputs={"input_data": Input(type=AssetTypes.URI_FOLDER)},
    outputs={"output_data": Output(type=AssetTypes.URI_FOLDER)},
    command="python ./pipeline-sequential/recognize_image.py --input_data ${{inputs.input_data}} --output_data ${{outputs.output_data}}",
    environment="form-rec-env:1",
    compute="cpu-cluster",
)

# DEFINE THE PIPELINE
@dsl.pipeline(compute='cpu-cluster')
def seq_pipeline(pdf_inputs):
    # using data_prep_function like a python call with its own inputs
    data_split_job = data_split_component(input_data=pdf_inputs,)

    # using train_func like a python call with its own inputs
    form_recognizer_job = form_recognizer_component(input_data=data_split_job.outputs.output_data)

    # a pipeline returns a dictionary of outputs
    # keys will code for the pipeline output identifier
    return {
        #"pipeline_data_split_job": data_split_job.outputs.output_data,
        "pipeline_ocr_output": form_recognizer_job.outputs.output_data,
    }

if __name__ == "__main__":

    # INSTANTIATE THE PIPELINE
    pipeline = seq_pipeline(pdf_inputs=Input(type=AssetTypes.URI_FOLDER, path="azureml://datastores/workspaceblobstore/paths/pdf-files/"))
    pipeline.outputs.pipeline_ocr_output = Output(type=AssetTypes.URI_FOLDER, path=ocr_store_path)

    # SUBMIT THE PIPELINE JOB
    pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="pipeline-sequential")
