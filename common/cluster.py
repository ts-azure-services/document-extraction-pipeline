# Script: one time script to create a cluster in Azure ML
import logging
from azure.ai.ml.entities import AmlCompute
from authenticate import ml_client

logging.basicConfig(level=logging.INFO)
# Specify aml compute name.
cpu_compute_target = "cpu-cluster"

try:
    ml_client.compute.get(cpu_compute_target)
    logging.info("Compute target already created.")
except Exception:
    logging.info("Creating a new cpu compute target...")
    compute = AmlCompute(name=cpu_compute_target,
                         size="STANDARD_DS3_V2",
                         min_instances=1,
                         max_instances=3)
    ml_client.compute.begin_create_or_update(compute)
