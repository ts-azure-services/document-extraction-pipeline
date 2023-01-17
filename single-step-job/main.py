import os.path
from azure.ai.ml import command
from azure.ai.ml.entities import Data
from azure.ai.ml import Input, Output
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import ml_client


if __name__ == "__main__":

    my_job_inputs = {"input_data": Input(
        type=AssetTypes.URI_FOLDER,
        path="azureml://datastores/workspaceblobstore/paths/pdf-files/")
                     }
    my_job_outputs = {"output_data": Output(
        type=AssetTypes.URI_FOLDER,
        path="azureml://datastores/workspaceblobstore/paths/pdf-images/")
                      }

    job = command(
        code="./single-step-job/",  # local path where the code is stored
        inputs=my_job_inputs,
        outputs=my_job_outputs,
        command="python pdf_to_png.py \
                --input ${{inputs.input_data}} \
                --output ${{outputs.output_data}}",
        environment="pdf-split-env:1",
        compute="cpu-cluster",
    )

    # Submit the command
    returned_job = ml_client.jobs.create_or_update(job)
