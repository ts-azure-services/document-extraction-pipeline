import argparse
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import command, dsl, Input, Output
from azure.ai.ml.parallel import parallel_run_function, RunFunction
import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import ml_client, auth_var


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_datastore", type=str)
    parser.add_argument("--intermediate_pdf_datastore", type=str)
    parser.add_argument("--intermediate_txt_datastore", type=str)
    parser.add_argument("--output_datastore", type=str)
    args = parser.parse_args()

    # Cleanup all files in intermediate locations, except the source container
    delete_intermediate_components = command(
        code="./",
        name="delete_existing_files",
        display_name="Delete existing files in intermediate locations",
        description="Delete existing files in intermediate locations",
        inputs=dict(page_pdf_container=Input(type='string'),
                    page_txt_container=Input(type='string'),
                    final_txt_container=Input(type='string'),
                    ),
        outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER, path=args.input_datastore)),
        command="python ./pipeline-parallel/erase.py \
            --page_pdf_container ${{inputs.page_pdf_container}} \
            --page_txt_container ${{inputs.page_txt_container}} \
            --final_txt_container ${{inputs.final_txt_container}} \
            --job_output_path ${{outputs.job_output_path}}",
        environment="blob-env:1",
        compute="cpu-cluster",
        is_deterministic=True,
    )

    # Split PDFs into page-level PDFs
    pdf_parallel_component = parallel_run_function(
        name="process_pdfs",
        display_name="Split PDFs into single PDF pages",
        description="Split PDFs into single PDF pages",
        inputs=dict(job_data_path=Input(type=AssetTypes.URI_FOLDER,)),
        input_data="${{inputs.job_data_path}}",
        outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER)),
        instance_count=3,
        max_concurrency_per_instance=4,
        mini_batch_size="1",
        mini_batch_error_threshold=1,
        retry_settings=dict(max_retries=5, timeout=600),
        logging_level="DEBUG",
        task=RunFunction(
            code="./",
            entry_script="./pipeline-parallel/pdf_to_image_entry.py",
            program_arguments="--job_output_path ${{outputs.job_output_path}}",
            environment="parallel-env:1",
        ),
        is_deterministic=True,
    )

    # Extract text from PDFs
    ocr_convert_component = parallel_run_function(
        name="convert_images_to_ocr",
        display_name="Extract single text files from single PDFs",
        description="Extract single text files from single PDFs",
        inputs=dict(job_data_path=Input(type=AssetTypes.URI_FOLDER,)),
        input_data="${{inputs.job_data_path}}",
        outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER)),# path=blob_store_path)),
        instance_count=3,
        max_concurrency_per_instance=4,
        mini_batch_size="1",
        mini_batch_error_threshold=1,
        retry_settings=dict(max_retries=5, timeout=600),
        logging_level="DEBUG",
        task=RunFunction(
            code="./",
            entry_script="./pipeline-parallel/png_to_ocr_entry.py",
            program_arguments="--job_output_path ${{outputs.job_output_path}}",
            environment="form-rec-env:1",
        ),
        is_deterministic=True,
    )

    # Consolidate all the discrete text files into one text file
    consolidate_txt_files = command(
        code="./",
        name="consolidate_text_files",
        display_name="Consolidate discrete text files into one text file",
        description="Consolidate discrete text files into one text file",
        inputs=dict(input_path=Input(type=AssetTypes.URI_FOLDER,)),
        input_data="${{inputs.input_path}}",
        outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER, path=args.output_datastore)),
        command="python ./pipeline-parallel/consolidate_files.py \
            --input_path ${{inputs.input_path}} \
            --job_output_path ${{outputs.job_output_path}}",
        environment="blob-env:1",
        compute="cpu-cluster",
        is_deterministic=True,
    )

    # DEFINE THE PIPELINE
    @dsl.pipeline(compute='cpu-cluster')
    def par_pipeline(page_pdf_container, page_txt_container, final_txt_container):

        # Delete intermediate files
        delete_intermediate_files = delete_intermediate_components(
                page_pdf_container = page_pdf_container,
                page_txt_container = page_txt_container,
                final_txt_container = final_txt_container,
        )
        # Initiate the step to break up large PDFs into pages
        process_pdfs = pdf_parallel_component(job_data_path=delete_intermediate_files.outputs.job_output_path)

        # Solution 1; remove the line below, to let the setting for blob_store_path defined above persist
        # return {"pipeline_job_output":process_pdfs.outputs.job_output_path}

        ocr_conversion = ocr_convert_component(job_data_path=process_pdfs.outputs.job_output_path)

        consolidate_files = consolidate_txt_files(input_path=ocr_conversion.outputs.job_output_path)

        # Solution 2; return the process_pdfs, but after instantiation, set path to blob_store_path
        return {"pdf_job_output": process_pdfs.outputs.job_output_path,
                "ocr_job_output": ocr_conversion.outputs.job_output_path
                }

    # Instantiate the pipeline
    pipeline = par_pipeline(page_pdf_container=auth_var['blob_container_images'],
                            page_txt_container=auth_var['blob_container_txt'],
                            final_txt_container=auth_var['blob_container_final'],
                            )
    pipeline.outputs.pdf_job_output = Output(type=AssetTypes.URI_FOLDER, path=args.intermediate_pdf_datastore)
    pipeline.outputs.ocr_job_output = Output(type=AssetTypes.URI_FOLDER, path=args.intermediate_txt_datastore)

    # Submit the pipeline job
    pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="pipeline-parallel",)
