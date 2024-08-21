import re
import yaml
from yaml_constructors import LookObject, DashboardObject


class ContentManager:
    MODEL_NAME = "bi_carelogic"

    def __init__(self):
        self.current_content = []
        self.consolidated_content = []

    # Load content, excluding customer folders not in customer_include_list
    def load_content(self, content_path: str, folder_mapping):
        self.folder_mapping = folder_mapping

        with open(content_path, "r", encoding="utf-8") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)

        if content is None:
            self.current_content = []
            return

        content[:] = [
            c for c in content if self._is_in_customer_included_folder(c)]
        self.current_content = content
        self.consolidated_content.extend(content)

    def update_content_folder_ids(self):
        for c in self.current_content:
            if isinstance(c, LookObject):
                # Update the folder ID
                new_folder_id = self.folder_mapping[c.legacy_folder_id]["new_id"]
                c.legacy_folder_id = str(new_folder_id)

                # Update model
                c.query_obj["model"] = self.MODEL_NAME

                # Update project
                self._update_project_name_for_look(c)
            elif isinstance(c, DashboardObject):
                # Update the folder ID
                new_folder_id = self.folder_mapping[c.legacy_folder_id["folder_id"]][
                    "new_id"
                ]
                c.legacy_folder_id["folder_id"] = str(new_folder_id)

                # Update model
                model_pattern = re.compile(r"model:\s+\S+\n")
                c.lookml = model_pattern.sub(
                    f"model: {self.MODEL_NAME}\n", c.lookml)

                # Update project
                c.lookml = re.sub(
                    r"(project_name:\s*)(\\?n\s*)?[^\\n]*_carelogic\b",
                    r"\1standard_carelogic",
                    c.lookml,
                )

    def get_consolidated_content(self):
        return self.consolidated_content

    def get_current_content(self):
        return self.current_content

    def get_current_dashboards(self):
        return [d for d in self.current_content if isinstance(d, DashboardObject)]

    def _update_project_name_for_look(self, obj):
        # Hard-coded values
        old_suffix = "_carelogic"
        new_name = "standard_carelogic"

        # If the object is an instance of LookObject
        if isinstance(obj, LookObject):
            # Iterate through all attributes of the LookObject
            for attr_name in dir(obj):
                # Skip special methods and properties
                if attr_name.startswith("__") or callable(getattr(obj, attr_name)):
                    continue

                attr_value = getattr(obj, attr_name)

                # Recurse into dictionaries or lists if needed
                if isinstance(attr_value, dict) or isinstance(attr_value, list):
                    self._update_project_name_for_look(attr_value)
                # If the attribute is a string and is a project_name ending in old_suffix, replace it
                elif (
                    isinstance(attr_value, str)
                    and attr_name == "project_name"
                    and attr_value.endswith(old_suffix)
                ):
                    setattr(obj, attr_name, new_name)

        # If the object is a dictionary, iterate through its keys and values
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if (
                    key == "project_name"
                    and isinstance(value, str)
                    and value.endswith(old_suffix)
                ):
                    obj[key] = new_name
                else:
                    self._update_project_name_for_look(value)

        # If the object is a list, iterate through its items
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                self._update_project_name_for_look(item)

    def _is_in_customer_included_folder(self, c):
        if isinstance(c, LookObject):
            return c.legacy_folder_id in self.folder_mapping
        return c.legacy_folder_id["folder_id"] in self.folder_mapping
