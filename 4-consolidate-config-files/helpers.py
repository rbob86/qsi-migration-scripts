import csv
import yaml
import looker_sdk
import os


def load_api_keys(csv_filename):
    api_keys = {}
    with open(csv_filename, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            instance_id = row["looker_url"].split("//")[1].split(".")[0]
            api_keys[instance_id] = {
                "client_id": row["client_id"],
                "client_secret": row["client_secret"],
            }
    return api_keys


def write_output(output_dir, folders, content):
    settings_path = os.path.join(output_dir, "settings.yaml")
    content_path = os.path.join(output_dir, "content.yaml")

    os.makedirs(output_dir, exist_ok=True)

    # Write settings file
    with open("base-settings.yaml", "r") as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)
    settings.append(folders)
    with open(settings_path, "w") as file:
        yaml.dump(settings, file, default_flow_style=False)

    # Write content file
    with open(content_path, "w") as file:
        yaml.dump(content, file, default_flow_style=False)


def get_user_info_from_looker(sdk, owner_id):
    user = sdk.user(owner_id)
    external_user_id = (
        user.credentials_embed[0].external_user_id
        if len(user.credentials_embed)
        else user.email
    )
    user_attributes = sdk.user_attribute_user_values(user.id)
    attributes_to_extract = [
        "allowed_customer_schemas",
        "signed_in_org",
        "staff_id",
    ]
    user_attribute_values = {attr: None for attr in attributes_to_extract}

    for attr in user_attributes:
        if attr["name"] in attributes_to_extract:
            user_attribute_values[attr["name"]] = attr["value"]

    org_name = user_attribute_values["allowed_customer_schemas"].split("_")[0].upper()
    group_name = f"{org_name}_Writer"

    return {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_attributes": user_attribute_values,
        "external_user_id": external_user_id,
        "group_name": group_name,
    }
