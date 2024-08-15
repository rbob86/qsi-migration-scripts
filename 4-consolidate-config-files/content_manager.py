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

        with open(content_path, "r") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)

        content[:] = [c for c in content if self._is_in_customer_included_folder(c)]
        self.current_content = content
        self.consolidated_content.extend(content)

    def update_content_folder_ids(self):
        for c in self.current_content:
            if isinstance(c, LookObject):
                new_folder_id = self.folder_mapping[c.legacy_folder_id]["new_id"]
                c.legacy_folder_id = str(new_folder_id)
                c.query_obj["model"] = self.MODEL_NAME
            elif isinstance(c, DashboardObject):
                new_folder_id = self.folder_mapping[c.legacy_folder_id["folder_id"]][
                    "new_id"
                ]
                c.legacy_folder_id["folder_id"] = str(new_folder_id)
                model_pattern = re.compile(r"model:\s+\S+\n")
                c.lookml = model_pattern.sub(f"model: {self.MODEL_NAME}\n", c.lookml)

    def get_consolidated_content(self):
        return self.consolidated_content

    def get_current_content(self):
        return self.current_content

    def get_current_dashboards(self):
        return [d for d in self.current_content if isinstance(d, DashboardObject)]

    def _is_in_customer_included_folder(self, c):
        if isinstance(c, LookObject):
            return c.legacy_folder_id in self.folder_mapping
        return c.legacy_folder_id["folder_id"] in self.folder_mapping
