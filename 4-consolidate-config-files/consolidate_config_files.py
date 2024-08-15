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


def main():
    # Read in command line arguments (instances, customers, output-dir)
    parser = argparse.ArgumentParser(
        description="Read in instances to parse and customer account names to consolidate."
    )
    parser.add_argument(
        "--instances",
        nargs="+",
        required=True,
        help="List of instances to parse config files for (e.g. qsi001 qsi002)",
    )
    parser.add_argument(
        "--customers",
        nargs="+",
        required=True,
        help="List of customer accounts to consolidate.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Name of output directory.",
    )
    args = parser.parse_args()

    instance_list = args.instances
    customer_include_list = args.customers
    output_dir = os.path.join("output", args.output_dir)

    # Create list of config folder directories to read from based on instance (qsi001, etc.)
    source_config_dirs = [
        f"../2-lmanage-capturator/config/config-{instance[-3:]}"
        for instance in instance_list
    ]

    # Create list of Looker API credentials for each instance
    api_keys = load_api_keys("../1-create-ini-files/looker-api-keys.csv")
    instances = [
        {
            "url": f"https://{instance}.cloud.looker.com",
            "client_id": api_keys[instance]["client_id"],
            "client_secret": api_keys[instance]["client_secret"],
        }
        for instance in instance_list
    ]

    # Initialize "global" variables
    all_owner_mapping = []

    folder_manager = FolderManager(customer_include_list)
    content_manager = ContentManager()

    for index, config_dir in enumerate(source_config_dirs):
        settings_path = os.path.join(config_dir, "settings.yaml")
        content_path = os.path.join(config_dir, "content.yaml")

        folder_manager.load_folders(settings_path)
        content_manager.load_content(content_path, folder_manager.folder_mapping)

        # Owner Mapping
        instance = instances[index]
        sdk = init_looker_sdk(instance)
        owner_mapping = {}
        folder_mapping = folder_manager.get_current_folder_mapping()
        dashboards = content_manager.get_current_dashboards()

        for dashboard in dashboards:
            scheduled_plans = dashboard.scheduled_plans
            alerts = dashboard.alerts

            if len(scheduled_plans) == 0 and len(alerts) == 0:
                continue

            dashboard_title_match = re.search(r"\btitle:\s*(.*)", dashboard.lookml)
            dashboard_title = dashboard_title_match.group(1).strip()
            folder_id = dashboard.legacy_folder_id["folder_id"]
            folder_name = folder_mapping[folder_id]["name"]
            parent_folder_id = folder_mapping[folder_id]["original_parent_id"]
            parent_folder_name = (
                "Shared"
                if parent_folder_id == "1"
                else folder_mapping[parent_folder_id]["name"]
            )

            for plan in scheduled_plans:
                owner_id = plan.user_id
                plan_to_save = {
                    "dashboard_title": dashboard_title,
                    "plan_name": plan.name,
                    "folder_name": folder_name,
                    "parent_folder_name": parent_folder_name,
                }

                if owner_id not in owner_mapping:
                    user_info = get_user_info_from_looker(sdk, owner_id)
                    owner_mapping[user_info["user_id"]] = {
                        "instance": instance["url"],
                        "first_name": user_info["first_name"],
                        "last_name": user_info["last_name"],
                        "user_attributes": user_info["user_attributes"],
                        "external_user_id": user_info["external_user_id"],
                        "group_name": user_info["group_name"],
                        "plans": [plan_to_save],
                    }
                else:
                    owner_mapping[owner_id]["plans"].append(plan_to_save)

            for alert in alerts:
                owner_id = alert.owner_id
                alert_to_save = {
                    "dashboard_title": dashboard_title,
                    "applied_dashboard_filters": alert.applied_dashboard_filters,
                    "cron": alert.cron,
                    "comparison_type": alert.comparison_type,
                    "threshold": alert.threshold,
                    "field_title": alert.field.title,
                    "field_name": alert.field.name,
                    "field_filter": alert.field.filter,
                    "folder_name": folder_name,
                    "parent_folder_name": parent_folder_name,
                }

                if owner_id not in owner_mapping:
                    user_info = get_user_info_from_looker(sdk, owner_id)
                    owner_mapping[user_info["user_id"]] = {
                        "instance": instance["url"],
                        "first_name": user_info["first_name"],
                        "last_name": user_info["last_name"],
                        "user_attributes": user_info["user_attributes"],
                        "external_user_id": user_info["external_user_id"],
                        "group_name": user_info["group_name"],
                        "alerts": [alert_to_save],
                    }
                else:
                    owner_mapping[owner_id]["alerts"].append(plan_to_save)

        for owner_info in owner_mapping.values():
            all_owner_mapping.append(owner_info)

        # Update content folder ids based on folder_mapping
        content_manager.update_content_folder_ids()

    # Save output files
    write_output(
        output_dir,
        folder_manager.get_consolidated_folder_hierarchy(),
        content_manager.get_consolidated_content(),
    )
    print(
        f"Successfully saved new content.yaml, settings.yaml files to directory {output_dir}"
    )

    # Save owner mapping file
    owner_mapping_filename = os.path.join(output_dir, "owner-mapping.json")
    with open(owner_mapping_filename, "w") as json_file:
        json.dump(all_owner_mapping, json_file, indent=4)


if __name__ == "__main__":
    main()
