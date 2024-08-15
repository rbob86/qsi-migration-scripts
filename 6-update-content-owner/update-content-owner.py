import json
import looker_sdk
import os
import requests
from looker_sdk import error, models40


def set_instance(instance):
    os.environ["LOOKERSDK_BASE_URL"] = instance["url"]
    os.environ["LOOKERSDK_CLIENT_ID"] = instance["client_id"]
    os.environ["LOOKERSDK_CLIENT_SECRET"] = instance["client_secret"]
    sdk = looker_sdk.init40()

    return sdk


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
    dashboard_info = user["plans"][0] if "plans" in user else user["alerts"][0]
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
        "external_user_id": user["external_user_id"],  # How is this formed?
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


target_instance = {
    "url": "https://looker-166.qualifacts.org",
    "client_id": "K5T8bZxNrHHysksMXdjd",
    "client_secret": "cgypSM5cYDXgpndKRpCRY9Nv",
}


with open("owner-mapping.json", "r") as json_file:
    owner_info = json.load(json_file)

folder_mapping = {}
sdk = set_instance(target_instance)
alerts = sdk.search_alerts()

for owner in owner_info:
    print(f"Updating owner to {owner['first_name']} {owner['last_name']}...")

    # Create folder name to id mapping
    item_details = owner["plans"] if "plans" in owner else owner["alerts"]
    for item in item_details:
        folder_key = get_folder_key(item["parent_folder_name"], item["folder_name"])
        if folder_key not in folder_mapping:
            add_folder_to_folder_mapping(sdk, folder_mapping, item)

    # Create embed user
    try:
        user_id = create_embed_user(sdk, target_instance["url"], owner, folder_mapping)
    except error.SDKError as e:
        print(e.message)

    if "plans" in owner:
        # Update owner for scheduled plans
        for plan in owner["plans"]:
            # Get dashboard
            dashboard = get_dashboard(plan, folder_mapping)

            # Get plan
            dashboard_plans = sdk.scheduled_plans_for_dashboard(
                dashboard.id, all_users=True
            )
            target_plan = [p for p in dashboard_plans if p.name == plan["plan_name"]][0]

            # Update plan owner
            sdk.update_scheduled_plan(
                scheduled_plan_id=target_plan.id,
                body=models40.WriteScheduledPlan(user_id=user_id),
            )

            print(
                f"\t{folder_key}/{dashboard.title} owner updated for scheduled plan \"{plan['plan_name']}\""
            )

    if "alerts" in owner:
        # Update owner for alerts
        for alert in owner["alerts"]:
            # Get dashboard elements
            dashboard = get_dashboard(alert, folder_mapping)
            dashboard_elements = sdk.dashboard_dashboard_elements(dashboard.id)
            dashboard_element_ids = [e.id for e in dashboard_elements]

            # Get alert
            target_alert = [
                a for a in alerts if is_alert_match(a, alert, dashboard_element_ids)
            ][0]

            # Update alert owner
            sdk.update_alert_field(
                alert_id=target_alert.id,
                body=models40.AlertPatch(owner_id=user_id),
            )

            print(f"\t{folder_key}/{dashboard.title} owner updated for alert")
