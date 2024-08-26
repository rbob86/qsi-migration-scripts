import argparse
import configparser
import csv
import os
import re
import looker_sdk
from looker_sdk import error
from looker_sdk.sdk.api40 import models

def parse_arguments():
    parser = argparse.ArgumentParser(description="Update Looker instance with new owner mappings.")
    parser.add_argument('--ini-file', required=True, help='Path to the ini file for the Looker SDK configuration.')
    parser.add_argument('--output-dir', required=True, help='Name of the subdirectory where the .csv output will be stored.')
    
    return parser.parse_args()

def get_base_url_from_ini(ini_file):
    config = configparser.ConfigParser()
    config.read(ini_file)

    # Assuming the ini file has a section like [Looker] or similar
    base_url = config.get('Looker', 'base_url')
    return base_url


def is_customer_group(s):
    pattern = r"^([a-zA-Z0-9]+)_(Viewer|Writer)$"
    match = re.match(pattern, s)
    if match:
        return match
    return None


def save_customer_details(customers, match, group, base_url):
    customer = match.group(1)
    group_type = match.group(2)
    group_obj = {"id": group["id"], "name": group["name"], "type": group_type}

    if customer in customers:
        customers[customer]["groups"].append(group_obj)
    else:
        try:
            folder_id = [f["id"] for f in folders if f["name"] == customer]
        except:
            print(f"Error: Could not determine folder id for customer {customer}")
        customers[customer] = {
            "instance": base_url,
            "groups": [group_obj],
            "folder_id": folder_id[0],
        }


def save_results_to_csv(customers, output_dir):
    # Create output_dir if not exist
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, "customer_mapping.csv")

    with open(filepath, "w", newline="") as csvfile:
        fieldnames = [
            "customer",
            "instance",
            "folder_id",
            "viewer_group_id",
            "writer_group_id",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for customer, info in customers.items():
            instance = info["instance"]
            folder_id = info["folder_id"]
            viewer_group_id = None
            writer_group_id = None

            for group in info["groups"]:
                if group["type"] == "Viewer":
                    viewer_group_id = group["id"]
                elif group["type"] == "Writer":
                    writer_group_id = group["id"]

            writer.writerow(
                {
                    "customer": customer,
                    "instance": instance,
                    "folder_id": folder_id,
                    "viewer_group_id": viewer_group_id,
                    "writer_group_id": writer_group_id,
                }
            )


if __name__ == "__main__":
    args = parse_arguments()

    # Load the Looker instance configuration from the ini file
    sdk = looker_sdk.init40(config_file=args.ini_file)
    shared_folder_id = "1"

    # Get output_dir
    output_dir = args.output_dir

    # Get Looker instance URL
    base_url = get_base_url_from_ini(args.ini_file)

    # Initialize Looker and get all objects
    groups = sdk.all_groups()
    folders = sdk.folder_children(folder_id=shared_folder_id)

    # Build customer objects, including folder id and group ids
    customers = {}
    for group in groups:
        match = is_customer_group(group["name"])

        if match:
            save_customer_details(customers, match, group, base_url)

    if not len(customers):
        print("No customer accounts found.")

    # Export results
    save_results_to_csv(customers, output_dir)

    print("Results saved to .csv")
