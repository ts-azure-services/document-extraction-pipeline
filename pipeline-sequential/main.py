import argparse
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import command, dsl, Input, Output
import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import ml_client


# Define paths for specific outputs
# blob_store_path="azureml://datastores/pdfinputfiles/paths/pdf-images/"
# ocr_store_path="azureml://datastores/textoutputfiles/paths/"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_datastore", type=str)
    parser.add_argument("--intermediate_datastore", type=str)
    parser.add_argument("--output_datastore", type=str)
    args = parser.parse_args()

    # Defining pipeline components
    data_split_component = command(
        code="./",
        inputs={"input_data": Input(type=AssetTypes.URI_FOLDER)},
        outputs={"output_data": Output(type=AssetTypes.URI_FOLDER, path=args.intermediate_datastore)},
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

    # Define the pipeline
    @dsl.pipeline(compute='cpu-cluster')
    def seq_pipeline(pdf_inputs):
        data_split_job = data_split_component(input_data=pdf_inputs,)
        form_recognizer_job = form_recognizer_component(input_data=data_split_job.outputs.output_data)
        return {
            "pipeline_ocr_output": form_recognizer_job.outputs.output_data,
        }

    pipeline = seq_pipeline(pdf_inputs=Input(type=AssetTypes.URI_FOLDER, path=args.input_datastore))
    pipeline.outputs.pipeline_ocr_output = Output(type=AssetTypes.URI_FOLDER, path=args.output_datastore)
    pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="pipeline-sequential")
