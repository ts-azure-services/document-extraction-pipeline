import argparse
import logging
from azure.ai.ml.entities import AzureBlobDatastore
from azure.ai.ml.entities import AccountKeyConfiguration
from authenticate import ml_client, auth_var

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--container_name", type=str)
    parser.add_argument("--datastore_name", type=str)
    parser.add_argument("--datastore_desc", type=str)
    args = parser.parse_args()

    try:
        store = AzureBlobDatastore(
            name=args.datastore_name,
            description=args.datastore_desc,
            account_name=auth_var['storage_account'],
            container_name=args.container_name,
            protocol="https",
            credentials=AccountKeyConfiguration(account_key=auth_var['storage_account_key']),
        )

        ml_client.create_or_update(store)
    except Exception as e:
        logging.info(f"Error: {e}")
