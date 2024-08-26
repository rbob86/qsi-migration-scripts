import argparse
import configparser
import json
import looker_sdk
import requests
from looker_sdk import error, models40


def parse_arguments():
    parser = argparse.ArgumentParser(description="Update Looker instance with new owner mappings.")
    parser.add_argument('--mapping', required=True, help='Path to the owner-mapping.json file.')
    parser.add_argument('--ini-file', required=True, help='Path to the ini file for the Looker SDK configuration.')
    
    return parser.parse_args()


def get_base_url_from_ini(ini_file):
    config = configparser.ConfigParser()
    config.read(ini_file)

    # Assuming the ini file has a section like [Looker] or similar
    base_url = config.get('Looker', 'base_url')
    return base_url


def get_folder_key(parent_folder_name, folder_name):
    return f"{parent_folder_name}/{folder_name}"


def add_folder_to_folder_mapping(sdk, folder_mapping, item):
    if item["parent_folder_name"] == "Shared":
        parent_folder_id = "1"
    else:
        parent_folder = sdk.search_folders(name=item["parent_folder_name"])[0]
        parent_folder_id = parent_folder.id
    folder = sdk.search_folders(name=item["folder_name"], parent_id=parent_folder_id)[0]
    folder_id = folder.id
    folder_key = get_folder_key(item["parent_folder_name"], item["folder_name"])
    folder_mapping[folder_key] = folder_id


def create_embed_user(sdk, instance_url, user, folder_mapping):
    # Get group id
    group = sdk.search_groups(name=user["group_name"])[0]
    group_id = group.id

    # Find a dashboard id
    dashboard_info = user["plans"][0] if len(user["plans"]) > 0 else user["alerts"][0]
    folder_key = get_folder_key(
        dashboard_info["parent_folder_name"], dashboard_info["folder_name"]
    )
    dashboard_id = sdk.search_dashboards(
        title=dashboard_info["dashboard_title"], folder_id=folder_mapping[folder_key]
    )[0].id

    # Build user params
    params = {
        "target_url": f"{instance_url}/dashboards/{dashboard_id}",
        "session_length": 100,
        "external_user_id": user["external_user_id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "permissions": [
            "access_data",
            "clear_cache_refresh",
            "create_alerts",
            "create_custom_fields",
            "create_table_calculations",
            "download_without_limit",
            "embed_browse_spaces",
            "embed_save_shared_space",
            "explore",
            "save_content",
            "save_dashboards",
            "save_looks",
            "schedule_external_look_emails",
            "schedule_look_emails",
            "see_drill_overlay",
            "see_lookml_dashboards",
            "see_looks",
            "see_user_dashboards",
            "send_to_integration",
        ],
        "models": ["bi_carelogic"],
        "group_ids": [group_id],
        "user_attributes": user["user_attributes"],
    }

    # Send embed_sso_request to create user
    response = sdk.create_sso_embed_url(params)
    url = response.url
    requests.get(url)

    # Return newly created user's id
    return sdk.user_for_credential("embed", user["external_user_id"]).id


def get_dashboard(item, folder_mapping):
    folder_key = get_folder_key(item["parent_folder_name"], item["folder_name"])
    dashboard = sdk.search_dashboards(
        title=item["dashboard_title"], folder_id=folder_mapping[folder_key]
    )[0]
    return dashboard


def is_alert_match(alert_one, alert_two, dashboard_element_ids):
    is_dashboard_filter_match = set(alert_one.applied_dashboard_filters) == set(
        alert_two["applied_dashboard_filters"]
    )
    is_field_filter_match = set(alert_one.field.filter) == set(
        alert_two["field_filter"]
    )
    belongs_to_dashboard = alert_one.dashboard_element_id in dashboard_element_ids

    if (
        not is_dashboard_filter_match
        or not is_field_filter_match
        or not belongs_to_dashboard
    ):
        return False

    return (
        alert_one.cron == alert_two["cron"]
        and alert_one.comparison_type.value == alert_two["comparison_type"]
        and alert_one.threshold == alert_two["threshold"]
        and alert_one.field.title == alert_two["field_title"]
        and alert_one.field.name == alert_two["field_name"]
    )



if __name__ == "__main__":
    args = parse_arguments()

    # Load the Looker instance configuration from the ini file
    sdk = looker_sdk.init40(config_file=args.ini_file)

    # Load the owner mapping from the specified JSON file
    with open(args.mapping, "r") as json_file:
        owner_info = json.load(json_file)

    folder_mapping = {}
    base_url = get_base_url_from_ini(args.ini_file)
    alerts = sdk.search_alerts()

    for owner in owner_info:
        print(f"Updating owner to {owner['first_name']} {owner['last_name']}...")

        if len(owner["plans"]) > 0:
            item_details = owner["plans"]
            for item in item_details:
                folder_key = get_folder_key(item["parent_folder_name"], item["folder_name"])
                if folder_key not in folder_mapping:
                    add_folder_to_folder_mapping(sdk, folder_mapping, item)
        if len(owner["alerts"]) > 0:
            item_details = owner["alerts"]
            for item in item_details:
                folder_key = get_folder_key(item["parent_folder_name"], item["folder_name"])
                if folder_key not in folder_mapping:
                    add_folder_to_folder_mapping(sdk, folder_mapping, item)

        try:
            user_id = create_embed_user(sdk, base_url, owner, folder_mapping)
        except error.SDKError as e:
            print(e.message)

        if len(owner["plans"]) > 0:
            for plan in owner["plans"]:
                dashboard = get_dashboard(plan, folder_mapping)
                dashboard_plans = sdk.scheduled_plans_for_dashboard(
                    dashboard.id, all_users=True
                )
                target_plan = [p for p in dashboard_plans if p.name == plan["plan_name"]][0]

                sdk.update_scheduled_plan(
                    scheduled_plan_id=target_plan.id,
                    body=models40.WriteScheduledPlan(user_id=user_id),
                )

                print(
                    f"\t{folder_key}/{dashboard.title} owner updated for scheduled plan \"{plan['plan_name']}\""
                )

        if len(owner["alerts"]) > 0:
            for alert in owner["alerts"]:
                dashboard = get_dashboard(alert, folder_mapping)
                dashboard_elements = sdk.dashboard_dashboard_elements(dashboard.id)
                dashboard_element_ids = [e.id for e in dashboard_elements]

                target_alert = [
                    a for a in alerts if is_alert_match(a, alert, dashboard_element_ids)
                ][0]

                sdk.update_alert_field(
                    alert_id=target_alert.id,
                    body=models40.AlertPatch(owner_id=user_id),
                )

                print(f"\t{folder_key}/{dashboard.title} owner updated for alert")