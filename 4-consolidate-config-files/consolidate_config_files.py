import argparse
import json
import looker_sdk
import os
import re
from content_manager import ContentManager
from folder_manager import FolderManager
from helpers import (
    load_api_keys,
    write_output,
    get_user_info_from_looker,
)


def init_looker_sdk(instance):
    os.environ["LOOKERSDK_BASE_URL"] = instance["url"]
    os.environ["LOOKERSDK_CLIENT_ID"] = instance["client_id"]
    os.environ["LOOKERSDK_CLIENT_SECRET"] = instance["client_secret"]
    return looker_sdk.init40()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Read in instances to parse and customer account names to consolidate."
    )
    parser.add_argument(
        "-i",
        "--instances",
        nargs="+",
        required=True,
        help="List of instances to parse config files for (e.g. qsi001 qsi002)",
    )
    parser.add_argument(
        "-c",
        "--customers",
        nargs="+",
        required=True,
        help="List of customer accounts to consolidate.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Name of output directory.",
    )
    return parser.parse_args()


def prepare_instances(instance_list, api_keys):
    return [
        {
            "url": f"https://{instance}.cloud.looker.com",
            "client_id": api_keys[instance]["client_id"],
            "client_secret": api_keys[instance]["client_secret"],
        }
        for instance in instance_list
    ]


def get_dashboard_owner_mapping(sdk, dashboard, folder_mapping):
    owner_mapping = {}
    dashboard_title = extract_dashboard_title(dashboard.lookml)
    folder_info = get_folder_info(
        dashboard.legacy_folder_id["folder_id"], folder_mapping
    )

    for plan in dashboard.scheduled_plans:
        update_owner_mapping(
            owner_mapping,
            sdk,
            plan.user_id,
            plan,
            dashboard_title,
            folder_info,
            is_plan=True,
        )

    for alert in dashboard.alerts:
        update_owner_mapping(
            owner_mapping,
            sdk,
            alert.owner_id,
            alert,
            dashboard_title,
            folder_info,
            is_plan=False,
        )

    return owner_mapping


def extract_dashboard_title(lookml):
    match = re.search(r"\btitle:\s*(.*)", lookml)
    return match.group(1).strip() if match else "Untitled"


def get_folder_info(folder_id, folder_mapping):
    folder_name = folder_mapping[folder_id]["name"]
    parent_folder_id = folder_mapping[folder_id]["original_parent_id"]
    parent_folder_name = (
        "Shared"
        if parent_folder_id == "1"
        else folder_mapping[parent_folder_id]["name"]
    )
    return {"folder_name": folder_name, "parent_folder_name": parent_folder_name}


def update_owner_mapping(
    owner_mapping, sdk, owner_id, item, dashboard_title, folder_info, is_plan=True
):
    item_to_save = {
        "dashboard_title": dashboard_title,
        "folder_name": folder_info["folder_name"],
        "parent_folder_name": folder_info["parent_folder_name"],
    }

    if is_plan:
        item_to_save.update({"plan_name": item.name})
    else:
        item_to_save.update(
            {
                "cron": item.cron,
                "comparison_type": item.comparison_type,
                "threshold": item.threshold,
                "field_title": item.field.title,
                "field_name": item.field.name,
                "field_filter": [f.__dict__ for f in item.field.filter],
            }
        )

    if owner_id not in owner_mapping:
        user_info = get_user_info_from_looker(sdk, owner_id)
        owner_mapping[user_info["user_id"]] = {
            "instance": sdk.auth.settings.base_url,
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
            "user_attributes": user_info["user_attributes"],
            "external_user_id": user_info["external_user_id"],
            "group_name": user_info["group_name"],
            "plans": [item_to_save] if is_plan else [],
            "alerts": [item_to_save] if not is_plan else []
        }
    else:
        owner_mapping[owner_id]["plans" if is_plan else "alerts"].append(item_to_save)


def consolidate_owner_mapping(owner_mapping_list):
    consolidated_mapping = {}

    for owner_mapping in owner_mapping_list:
        external_user_id = owner_mapping["external_user_id"]

        if external_user_id not in consolidated_mapping:
            consolidated_mapping[external_user_id] = {
                "instance": owner_mapping["instance"],
                "first_name": owner_mapping["first_name"],
                "last_name": owner_mapping["last_name"],
                "user_attributes": owner_mapping["user_attributes"],
                "external_user_id": external_user_id,
                "group_name": owner_mapping["group_name"],
                "plans": [],
                "alerts": [],
            }

        if "plans" in owner_mapping:
            consolidated_mapping[external_user_id]["plans"].extend(owner_mapping["plans"])
        if "alerts" in owner_mapping:
            consolidated_mapping[external_user_id]["alerts"].extend(owner_mapping["alerts"])

    return list(consolidated_mapping.values())


def main():
    args = parse_arguments()
    instance_list = args.instances
    customer_include_list = args.customers
    output_dir = os.path.join("output", args.output_dir)

    source_config_dirs = [
        f"../2-lmanage-capturator/config/config-{instance[-3:]}"
        for instance in instance_list
    ]
    api_keys = load_api_keys("../1-create-ini-files/looker-api-keys.csv")
    instances = prepare_instances(instance_list, api_keys)

    all_owner_mapping = []
    folder_manager = FolderManager(customer_include_list)
    content_manager = ContentManager()

    for index, config_dir in enumerate(source_config_dirs):
        settings_path = os.path.join(config_dir, "settings.yaml")
        content_path = os.path.join(config_dir, "content.yaml")

        folder_manager.load_folders(settings_path)
        content_manager.load_content(content_path, folder_manager.folder_mapping)

        instance = instances[index]
        sdk = init_looker_sdk(instance)
        folder_mapping = folder_manager.get_current_folder_mapping()
        dashboards = content_manager.get_current_dashboards()

        for dashboard in dashboards:
            owner_mapping = get_dashboard_owner_mapping(sdk, dashboard, folder_mapping)
            all_owner_mapping.extend(owner_mapping.values())

        content_manager.update_content_folder_ids()

    write_output(
        output_dir,
        folder_manager.get_consolidated_folder_hierarchy(),
        content_manager.get_consolidated_content(),
    )
    print(
        f"Successfully saved new content.yaml, settings.yaml files to directory {output_dir}"
    )

    consolidated_owner_mapping = consolidate_owner_mapping(all_owner_mapping)

    owner_mapping_filename = os.path.join(output_dir, "owner-mapping.json")
    with open(owner_mapping_filename, "w") as json_file:
        json.dump(consolidated_owner_mapping, json_file, indent=4)


if __name__ == "__main__":
    main()
