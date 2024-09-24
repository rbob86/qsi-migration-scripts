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

class AlertAppliedDashboardFilterObject:
    def __init__(self, filter_title, field_name, filter_value, filter_description):
        self.filter_title = filter_title
        self.field_name = field_name
        self.filter_value = filter_value
        self.filter_description = filter_description

class AlertFieldFilterObject:
    def __init__(self, field_name, field_value, filter_value):
        self.field_name = field_name
        self.field_value = field_value
        self.filter_value = filter_value

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
    filters = values.pop("filter", [])
    if filters:
        filters = [
            AlertFieldFilterObject(**f) if isinstance(f, dict) else f
            for f in filters
        ]
    values["filter"] = filters
    return AlertFieldObject(**values)


def construct_alert_field_filter_object(loader, node):
    values = loader.construct_mapping(node)
    return AlertFieldFilterObject(**values)


def construct_alert_destination_object(loader, node):
    values = loader.construct_mapping(node)
    return AlertDestinationObject(**values)


def construct_alert_applied_dashboard_filter_object(loader, node):
    values = loader.construct_mapping(node)
    return AlertAppliedDashboardFilterObject(**values)


def construct_alert_object(loader, node):
    values = loader.construct_mapping(node)
    destinations = values.pop("destinations", [])
    if destinations:
        destinations = [
            AlertDestinationObject(**dest) if isinstance(dest, dict) else dest
            for dest in destinations
        ]
    dashboard_filters = values.pop("applied_dashboard_filters", [])
    if dashboard_filters:
        dashboard_filters = [
            AlertAppliedDashboardFilterObject(**d) if isinstance(d, dict) else d
            for d in dashboard_filters
        ]
    field = values.pop("field", None)
    if field and not isinstance(field, AlertFieldObject):
        field = AlertFieldObject(**field)
    values["destinations"] = destinations
    values["field"] = field
    values["applied_dashboard_filters"] = dashboard_filters
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


def represent_alert_applied_dashboard_filter_object(dumper, data):
    return dumper.represent_mapping("!AlertAppliedDashboardFilterObject", data.__dict__)


def represent_alert_field_filter_object(dumper, data):
    return dumper.represent_mapping("!AlertFieldFilterObject", data.__dict__)


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
yaml.add_constructor("!AlertAppliedDashboardFilterObject", construct_alert_applied_dashboard_filter_object)
yaml.add_constructor("!AlertFieldFilterObject", construct_alert_field_filter_object)
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
yaml.add_representer(AlertAppliedDashboardFilterObject, represent_alert_applied_dashboard_filter_object)
yaml.add_representer(AlertFieldFilterObject, represent_alert_field_filter_object)
yaml.add_representer(AlertDestinationObject, represent_alert_destination_object)
yaml.add_representer(AlertObject, represent_alert_object)
yaml.add_representer(DashboardObject, represent_dashboard_object)
yaml.add_representer(LookObject, represent_look_object)

# For saving empty values as empty as opposed to '' or null
yaml.add_representer(type(None), none_to_empty_str_representer)
