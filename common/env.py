import argparse
from azure.ai.ml.entities import Environment
from authenticate import ml_client

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument("-i", "--image", default="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04", type=str)
    parser.add_argument("-i", "--image", default="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04", type=str)
    parser.add_argument("-cf", "--conda_file", default="./config/conda.yml", type=str)
    parser.add_argument("-n", "--name", default="Custom-Environment", type=str)
    parser.add_argument("-v", "--version", type=str)
    parser.add_argument("-d", "--description", default="Env created from a Docker image + Conda env", type=str)
    args = parser.parse_args()

    try:
        env_docker_conda = Environment(
                image=args.image,
                conda_file=args.conda_file,
                name=args.name,
                version=args.version,
                description=args.description
                )
        ml_client.environments.create_or_update(env_docker_conda)
    except Exception as e:
        print(f"Error: {e}")
