# ai-document-extraction-pipeline
This repo is inspired by the design approach laid out by [Alexandre Delarue](https://github.com/aldelar) in his
  [aml-documents-extraction](https://github.com/aldelar/aml-documents-extraction) repo. This architectural
  approach leverages Azure Machine Learning's pipeline infrastructure to orchestrate a flexible document
  enrichment pipeline. This repo follows a similar approach. However, it seeks to demonstrate a more gradual
  approach to building a parallel pipeline, starting from a single job to a sequential pipeline and then to a
  parallel pipeline. It also is
  updated for the use of the Azure ML Python SDK v2, which went generally available in mid-2022.
  
A document enrichment pipeline typically has both an extraction and enrichment pattern. Both pipeline
workflows below demonstrate this in single steps. 

The key workflows are in three stages, which map to the folder structure:
- `single-step-job`. This is a demonstration of a single job that takes PDF files, and breaks it into discrete images.
- `pipeline-sequential`. This is a demonstration of a sequential pipeline which first takes PDF files, breaks
  it into images, and then leverages [Azure Form
  Recognizer](https://azure.microsoft.com/en-us/products/form-recognizer/) and a pre-built model to perform
  OCR recognition to pull out text. A visual illustration of this process is shown below.
  ![sequential-pipeline](./imgs/sequential-pipeline.jpg)
- `pipeline-parallel`. This is a demonstration of the sequential pipeline, but each step is parallelized. This
  allows for horizontal scaling and faster processing. To understand more about parallel processing in
  Azure ML, refer this
  [documentation](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-job-in-pipeline?tabs=cliv2).
  A visual illustration of this process is shown below.
  ![parallel-pipeline](./imgs/parallel-pipeline.jpg)

### Initial Setup
- While one can create a separate ADLS to be the data repository for the pipeline, I opted to convert the
  default blobstore created through the Azure Machine Learning provisioning process into an ADLS Gen 2
  resource. This can be manually done in the Portal by changing the Hierarchial namespace from
  `Disabled` to `Enabled`. This is a process that is non-reversible. Preferably, do this after
  creating the cluster and the environments in Azure ML. This allows for artifacts to settle in the default blobstore
  before being converted.
- For the data inputs, manually create a folder called `pdf-files` in the ADLS Gen 2 store created above. This
  can also be automated. For sample PDFs, refer to [arxiv](https://arxiv.org).
- For the steps in mimicking the above, refer the `Makefile`.

### Other Considerations
- Number of documents to process.
- Size of individual documents to process.

#### Future 
- Automate the upload of PDF files to ADLS Gen 2
- Create a bash script that ensures all PDF file names have no open spaces
- To test performance, create a bash script to duplicate PDF files
- Ensuring environment variables can be read in the parallel entry script.
