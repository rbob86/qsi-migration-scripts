import argparse
import csv
import json
import sys
import looker_sdk
import os
import re
import yaml


# Define YAML object classes
class LookerPermissionSet:
    def __init__(self, permissions, name):
        self.permissions = permissions
        self.name = name


class LookerModelSet:
    def __init__(self, models, name):
        self.models = models
        self.name = name


class LookerRoles:
    def __init__(self, permission_set, model_set, teams, name):
        self.permission_set = permission_set
        self.model_set = model_set
        self.teams = teams
        self.name = name


class LookerUserAttribute:
    def __init__(
        self, name, uatype, hidden_value, user_view, user_edit, default_value, teams
    ):
        self.name = name
        self.uatype = uatype
        self.hidden_value = hidden_value
        self.user_view = user_view
        self.user_edit = user_edit
        self.default_value = default_value
        self.teams = teams


class LookerFolder:
    def __init__(
        self, content_metadata_id, id, name, parent_id, subfolder, team_edit, team_view
    ):
        self.content_metadata_id = content_metadata_id
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.subfolder = subfolder
        self.team_edit = team_edit
        self.team_view = team_view


class UserPublic:
    def __init__(self, can, id, first_name, last_name, display_name, avatar_url, url):
        self.can = can
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.url = url


class ScheduledPlanDestination:
    def __init__(
        self,
        id,
        scheduled_plan_id,
        format,
        apply_formatting,
        apply_vis,
        address,
        looker_recipient,
        type,
        parameters,
        secret_parameters,
        message,
    ):
        self.id = id
        self.scheduled_plan_id = scheduled_plan_id
        self.format = format
        self.apply_formatting = apply_formatting
        self.apply_vis = apply_vis
        self.address = address
        self.looker_recipient = looker_recipient
        self.type = type
        self.parameters = parameters
        self.secret_parameters = secret_parameters
        self.message = message


class ScheduledPlan:
    def __init__(
        self,
        name,
        user_id,
        run_as_recipient,
        enabled,
        look_id,
        dashboard_id,
        lookml_dashboard_id,
        filters_string,
        dashboard_filters,
        require_results,
        require_no_results,
        require_change,
        send_all_results,
        crontab,
        datagroup,
        timezone,
        query_id,
        scheduled_plan_destination,
        run_once,
        include_links,
        custom_url_base,
        custom_url_params,
        custom_url_label,
        show_custom_url,
        pdf_paper_size,
        pdf_landscape,
        embed,
        color_theme,
        long_tables,
        inline_table_width,
        id,
        created_at,
        updated_at,
        title,
        user,
        next_run_at,
        last_run_at,
        can,
    ):
        self.name = name
        self.user_id = user_id
        self.run_as_recipient = run_as_recipient
        self.enabled = enabled
        self.look_id = look_id
        self.dashboard_id = dashboard_id
        self.lookml_dashboard_id = lookml_dashboard_id
        self.filters_string = filters_string
        self.dashboard_filters = dashboard_filters
        self.require_results = require_results
        self.require_no_results = require_no_results
        self.require_change = require_change
        self.send_all_results = send_all_results
        self.crontab = crontab
        self.datagroup = datagroup
        self.timezone = timezone
        self.query_id = query_id
        self.scheduled_plan_destination = scheduled_plan_destination
        self.run_once = run_once
        self.include_links = include_links
        self.custom_url_base = custom_url_base
        self.custom_url_params = custom_url_params
        self.custom_url_label = custom_url_label
        self.show_custom_url = show_custom_url
        self.pdf_paper_size = pdf_paper_size
        self.pdf_landscape = pdf_landscape
        self.embed = embed
        self.color_theme = color_theme
        self.long_tables = long_tables
        self.inline_table_width = inline_table_width
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.title = title
        self.user = user
        self.next_run_at = next_run_at
        self.last_run_at = last_run_at
        self.can = can


class AlertFieldObject:
    def __init__(self, title, name, filter):
        self.title = title
        self.name = name
        self.filter = filter


class AlertDestinationObject:
    def __init__(self, destination_type, email_address):
        self.destination_type = destination_type
        self.email_address = email_address


class AlertObject:
    def __init__(
        self,
        applied_dashboard_filters,
        comparison_type,
        cron,
        custom_title,
        description,
        destinations,
        field,
        is_disabled,
        is_public,
        disabled_reason,
        threshold,
        owner_id,
    ):
        self.applied_dashboard_filters = applied_dashboard_filters
        self.comparison_type = comparison_type
        self.cron = cron
        self.custom_title = custom_title
        self.description = description
        self.destinations = destinations
        self.field = field
        self.is_disabled = is_disabled
        self.is_public = is_public
        self.disabled_reason = disabled_reason
        self.threshold = threshold
        self.owner_id = owner_id


class DashboardObject:
    def __init__(
        self,
        legacy_folder_id,
        lookml,
        dashboard_id,
        dashboard_slug,
        dashboard_element_alert_counts,
        scheduled_plans,
        alerts,
    ):
        self.legacy_folder_id = legacy_folder_id
        self.lookml = lookml
        self.dashboard_id = dashboard_id
        self.dashboard_slug = dashboard_slug
        self.dashboard_element_alert_counts = dashboard_element_alert_counts
        self.scheduled_plans = scheduled_plans
        self.alerts = alerts


class LookObject:
    def __init__(
        self, legacy_folder_id, look_id, title, query_obj, description, scheduled_plans
    ):
        self.legacy_folder_id = legacy_folder_id
        self.look_id = look_id
        self.title = title
        self.query_obj = query_obj
        self.description = description
        self.scheduled_plans = scheduled_plans


# Define YAML object constructors
def construct_looker_permission_set(loader, node):
    values = loader.construct_mapping(node)
    return LookerPermissionSet(**values)


def construct_looker_model_set(loader, node):
    values = loader.construct_mapping(node)
    return LookerModelSet(**values)


def construct_looker_roles(loader, node):
    values = loader.construct_mapping(node)
    return LookerRoles(**values)


def construct_looker_user_attribute(loader, node):
    values = loader.construct_mapping(node)
    return LookerUserAttribute(**values)


def construct_looker_folder(loader, node):
    values = loader.construct_mapping(node)
    subfolders = values.get("subfolder", [])
    if subfolders:
        values["subfolder"] = [
            construct_looker_folder(loader, subnode) for subnode in subfolders
        ]
    return LookerFolder(**values)


def construct_user_public(loader, node):
    values = loader.construct_mapping(node)
    return UserPublic(**values)


def construct_scheduled_plan_destination(loader, node):
    values = loader.construct_mapping(node)
    return ScheduledPlanDestination(**values)


def construct_scheduled_plan(loader, node):
    values = loader.construct_mapping(node)
    destinations = values.pop("scheduled_plan_destination", [])
    if destinations:
        destinations = [
            ScheduledPlanDestination(**dest) if isinstance(dest, dict) else dest
            for dest in destinations
        ]
    user = values.pop("user", None)
    if user and not isinstance(user, UserPublic):
        user = UserPublic(**user)
    values["scheduled_plan_destination"] = destinations
    values["user"] = user
    return ScheduledPlan(**values)


def construct_alert_field_object(loader, node):
    values = loader.construct_mapping(node)
    return AlertFieldObject(**values)


def construct_alert_destination_object(loader, node):
    values = loader.construct_mapping(node)
    return AlertDestinationObject(**values)


def construct_alert_object(loader, node):
    values = loader.construct_mapping(node)
    destinations = values.pop("destinations", [])
    if destinations:
        destinations = [
            AlertDestinationObject(**dest) if isinstance(dest, dict) else dest
            for dest in destinations
        ]
    field = values.pop("field", None)
    if field and not isinstance(field, AlertFieldObject):
        field = AlertFieldObject(**field)
    values["destinations"] = destinations
    values["field"] = field
    return AlertObject(**values)


def construct_dashboard_object(loader, node):
    values = loader.construct_mapping(node)
    scheduled_plans = values.get("scheduled_plans", [])
    if scheduled_plans:
        scheduled_plans = [
            ScheduledPlan(**plan) if isinstance(plan, dict) else plan
            for plan in scheduled_plans
        ]
    values["scheduled_plans"] = scheduled_plans
    return DashboardObject(**values)


def construct_look_object(loader, node):
    values = loader.construct_mapping(node)
    return LookObject(**values)


# Define representers for saving objects to YAML file
def represent_looker_permission_set(dumper, data):
    return dumper.represent_mapping("!LookerPermissionSet", data.__dict__)


def represent_looker_model_set(dumper, data):
    return dumper.represent_mapping("!LookerModelSet", data.__dict__)


def represent_looker_roles(dumper, data):
    return dumper.represent_mapping("!LookerRoles", data.__dict__)


def represent_looker_user_attribute(dumper, data):
    return dumper.represent_mapping("!LookerUserAttribute", data.__dict__)


def represent_looker_folder(dumper, data):
    return dumper.represent_mapping("!LookerFolder", data.__dict__)


def represent_user_public(dumper, data):
    return dumper.represent_mapping("!UserPublic", data.__dict__)


def represent_scheduled_plan_destination(dumper, data):
    return dumper.represent_mapping("!ScheduledPlanDestination", data.__dict__)


def represent_scheduled_plan(dumper, data):
    return dumper.represent_mapping("!ScheduledPlan", data.__dict__)


def represent_alert_field_object(dumper, data):
    return dumper.represent_mapping("!AlertFieldObject", data.__dict__)


def represent_alert_destination_object(dumper, data):
    return dumper.represent_mapping("!AlertDestinationObject", data.__dict__)


def represent_alert_object(dumper, data):
    return dumper.represent_mapping("!AlertObject", data.__dict__)


def represent_dashboard_object(dumper, data):
    return dumper.represent_mapping("!DashboardObject", data.__dict__)


def represent_look_object(dumper, data):
    return dumper.represent_mapping("!LookObject", data.__dict__)


def none_to_empty_str_representer(dumper, data):
    return dumper.represent_scalar(
        "tag:yaml.org,2002:null", "" if data is None else data
    )


# Register constructors
yaml.add_constructor("!LookerFolder", construct_looker_folder)
yaml.add_constructor("!LookerPermissionSet", construct_looker_permission_set)
yaml.add_constructor("!LookerModelSet", construct_looker_model_set)
yaml.add_constructor("!LookerRoles", construct_looker_roles)
yaml.add_constructor("!LookerUserAttribute", construct_looker_user_attribute)
yaml.add_constructor("!UserPublic", construct_user_public)
yaml.add_constructor("!ScheduledPlanDestination", construct_scheduled_plan_destination)
yaml.add_constructor("!ScheduledPlan", construct_scheduled_plan)
yaml.add_constructor("!AlertFieldObject", construct_alert_field_object)
yaml.add_constructor("!AlertDestinationObject", construct_alert_destination_object)
yaml.add_constructor("!AlertObject", construct_alert_object)
yaml.add_constructor("!DashboardObject", construct_dashboard_object)
yaml.add_constructor("!LookObject", construct_look_object)

yaml.add_representer(LookerFolder, represent_looker_folder)
yaml.add_representer(LookerPermissionSet, represent_looker_permission_set)
yaml.add_representer(LookerModelSet, represent_looker_model_set)
yaml.add_representer(LookerRoles, represent_looker_roles)
yaml.add_representer(LookerUserAttribute, represent_looker_user_attribute)
yaml.add_representer(UserPublic, represent_user_public)
yaml.add_representer(ScheduledPlanDestination, represent_scheduled_plan_destination)
yaml.add_representer(ScheduledPlan, represent_scheduled_plan)
yaml.add_representer(AlertFieldObject, represent_alert_field_object)
yaml.add_representer(AlertDestinationObject, represent_alert_destination_object)
yaml.add_representer(AlertObject, represent_alert_object)
yaml.add_representer(DashboardObject, represent_dashboard_object)
yaml.add_representer(LookObject, represent_look_object)

# For saving empty values as empty as opposed to '' or null
yaml.add_representer(type(None), none_to_empty_str_representer)


# Main functions
def compile_settings_and_write_to_file(folders: list[LookerFolder]):
    with open("base-settings.yaml", "r") as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    settings.extend(folders)

    with open("./output/settings.yaml", "w") as file:
        yaml.dump(settings, file, default_flow_style=False)


def map_folders_to_new_ids(folder: LookerFolder):
    global folder_counter
    global content_metadata_counter
    global folder_mapping
    global include_list

    if folder.parent_id == "1" and folder.name not in include_list:
        return

    folder_counter += 1
    content_metadata_counter += 1

    if folder.id == "1":
        for sub in folder.subfolder:
            map_folders_to_new_ids(sub)
        return

    parent_id = (
        folder_mapping[folder.parent_id]["id"]
        if folder.parent_id in folder_mapping
        else folder.parent_id
    )

    folder_mapping[folder.id] = {
        "id": folder_counter,
        "name": folder.name,
        "original_parent_id": folder.parent_id,
        "parent_id": parent_id,
    }
    folder.id = str(folder_counter)
    folder.parent_id = str(parent_id)
    folder.content_metadata_id = str(content_metadata_counter)

    for sub in folder.subfolder:
        map_folders_to_new_ids(sub)


def write_output(base_folder, folders, content):
    settings_path = os.path.join(base_folder, "settings.yaml")
    content_path = os.path.join(base_folder, "content.yaml")

    # Combine base settings with new folder structure
    with open("base-settings.yaml", "r") as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    settings.extend(folders)

    # Write settings file
    with open(settings_path, "w") as file:
        yaml.dump(settings, file, default_flow_style=False)

    # Write content file
    with open(content_path, "w") as file:
        yaml.dump(content, file, default_flow_style=False)


def get_user_info(sdk, owner_id):
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


OUTPUT_FOLDER = "./output"
MODEL_NAME = "bi_carelogic"

all_looker_folders = []
all_content = []
folder_counter = 0
content_metadata_counter = 0
all_owner_mapping = []
include_list = []


def load_api_keys(csv_filename):
    api_keys = {}
    with open(csv_filename, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract the instance_id from the URL
            instance_id = (
                row["looker_url"].split("//")[1].split(".")[0]
            )  # Extract 'qsi001' from 'https://qsi001.cloud.looker.com'
            api_keys[instance_id] = {
                "client_id": row["client_id"],
                "client_secret": row["client_secret"],
            }
    return api_keys


def main():
    parser = argparse.ArgumentParser(
        description="Read in customer account names to consolidate."
    )
    parser.add_argument(
        "--customers",
        nargs="+",
        required=True,
        help="List of customer accounts to consolidate",
    )
    parser.add_argument(
        "--instances",
        nargs="+",
        required=True,
        help="List of instance names to parse (e.g. qsi001 qsi002)",
    )
    args = parser.parse_args()

    include_list = args.customers
    instance_list = args.instances

    if len(include_list) == 0 or len(instance_list) == 0:
        return

    source_folders = [
        f"../2-lmanage-capturator/config/config-{instance[-3:]}"
        for instance in instance_list
    ]
    api_keys = load_api_keys("../1-create-ini-files/looker-api-keys.csv")
    instances = [
        {
            "url": f"https://{instance}.cloud.looker.com",
            "client_id": api_keys[instance]["client_id"],
            "client_secret": api_keys[instance]["client_secret"],
        }
        for instance in instance_list
    ]

    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    for base_folder in source_folders:
        settings_path = os.path.join(base_folder, "settings.yaml")
        content_path = os.path.join(base_folder, "content.yaml")

        # Extract folders and map new folder ids for content association
        with open(settings_path, "r") as file:
            settings_data = yaml.load(file, Loader=yaml.FullLoader)

        looker_folders = [
            item for item in settings_data if isinstance(item, LookerFolder)
        ]
        folder_mapping = {}

        map_folders_to_new_ids(looker_folders[0])

        # Add folders to overall folder structure
        shared_folder = looker_folders[0]
        shared_folder.subfolders = [
            s for s in shared_folder.subfolder if s.name in include_list
        ]

        if len(all_looker_folders):
            all_looker_folders[0].subfolder.extend(shared_folder.subfolders)
            team_view = all_looker_folders[0].team_view + shared_folder.team_view
            team_edit = all_looker_folders[0].team_edit + shared_folder.team_edit
            all_looker_folders[0].team_view = team_view
            all_looker_folders[0].team_edit = team_edit
        else:
            all_looker_folders.extend(looker_folders)

        def is_in_include_list(c):
            if isinstance(c, LookObject):
                return c.legacy_folder_id in folder_mapping
            return c.legacy_folder_id["folder_id"] in folder_mapping

        # Extract content and map to existing folder ids, combining team_view and team_edit values, and ignore content not in include_list
        with open(content_path, "r") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)
        content[:] = [c for c in content if is_in_include_list(c)]

        # Retrieve scheduled plan and owner information and save to JSON file
        instance_url = f"https://qsi{base_folder.split('-')[-1]}.cloud.looker.com"
        print(instances)
        instance = [i for i in instances if i["url"] == instance_url][0]
        os.environ["LOOKERSDK_BASE_URL"] = instance_url
        os.environ["LOOKERSDK_CLIENT_ID"] = instance["client_id"]
        os.environ["LOOKERSDK_CLIENT_SECRET"] = instance["client_secret"]
        sdk = looker_sdk.init40()
        owner_mapping = {}

        for c in content:
            if isinstance(c, LookObject):  # Only retrieve dashboard plans/alerts
                continue

            scheduled_plans = c.scheduled_plans
            alerts = c.alerts

            if len(scheduled_plans) or len(alerts):
                dashboard_title_match = re.search(r"\btitle:\s*(.*)", c.lookml)
                dashboard_title = dashboard_title_match.group(1).strip()
                folder_id = c.legacy_folder_id["folder_id"]
                folder_name = folder_mapping[folder_id]["name"]
                parent_folder_id = folder_mapping[folder_id]["original_parent_id"]

                if parent_folder_id == "1":
                    parent_folder_name = "Shared"
                else:
                    parent_folder_name = folder_mapping[parent_folder_id]["name"]

                for alert in alerts:
                    print(alert.description)

                for plan in scheduled_plans:
                    owner_id = plan.user_id

                    plan_to_save = {
                        "dashboard_title": dashboard_title,
                        "plan_name": plan.name,
                        "folder_name": folder_name,
                        "parent_folder_name": parent_folder_name,
                    }

                    if owner_id not in owner_mapping:
                        user_info = get_user_info(sdk, owner_id)

                        owner_mapping[user_info["user_id"]] = {
                            "instance": instance_url,
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
                        user_info = get_user_info(owner_id)

                        owner_mapping[user_info["user_id"]] = {
                            "instance": instance_url,
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

        # Update folder ids for content based on folder_mapping, and set model to "bi_carelogic"
        for c in content:
            if isinstance(c, LookObject):
                c.legacy_folder_id = str(folder_mapping[c.legacy_folder_id]["id"])
                c.query_obj["model"] = MODEL_NAME
            elif isinstance(c, DashboardObject):
                c.legacy_folder_id["folder_id"] = str(
                    folder_mapping[c.legacy_folder_id["folder_id"]]["id"]
                )
                model_pattern = re.compile(r"model:\s+\S+\n")
                c.lookml = model_pattern.sub("model: bi_carelogic\n", c.lookml)

        # Add content to overall content list
        all_content.extend(content)

    # Save scheduled_plan and alert owner mapping
    with open("owner-mapping.json", "w") as json_file:
        json.dump(all_owner_mapping, json_file, indent=4)
    print("Scheduled plan/alert to owner mapping has been saved to owner-mapping.json")

    # Save consolidated config file
    write_output(OUTPUT_FOLDER, all_looker_folders, all_content)


if __name__ == "__main__":
    main()
