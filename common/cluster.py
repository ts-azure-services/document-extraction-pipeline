"""This is a one-time setup script."""
# import sys
# import os.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))
from azure.ai.ml.entities import AmlCompute
from authenticate import ml_client

# Specify aml compute name.
cpu_compute_target = "cpu-cluster"

try:
    ml_client.compute.get(cpu_compute_target)
    print("Compute target already created.")
except Exception:
    print("Creating a new cpu compute target...")
    compute = AmlCompute(name=cpu_compute_target,
                         size="STANDARD_D2_V2",
                         min_instances=1,
                         max_instances=4)
    ml_client.compute.begin_create_or_update(compute)
