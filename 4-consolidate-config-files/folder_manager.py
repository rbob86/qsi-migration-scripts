import yaml
from yaml_constructors import LookerFolder


class FolderManager:
    SHARED_FOLDER_ID = "1"

    def __init__(self, customer_include_list):
        self.root_folder = None
        self.folder_counter = 0
        self.customer_include_list = customer_include_list
        self.folder_mapping = {}

    def load_folders(self, settings_path: str):
        # Load folders, excluding customer folders not in customer_include_list
        with open(settings_path, "r", encoding="utf-8") as file:
            settings_data = yaml.load(file, Loader=yaml.FullLoader)

        shared_folder = [
            item for item in settings_data if isinstance(item, LookerFolder)
        ][0]
        shared_folder.subfolder = self._filter_folders(shared_folder.subfolder)
        shared_folder.team_view = self._filter_folder_access_groups(
            shared_folder.team_view
        )

        # if first folder collection
        #   Initialize root_folder
        # else
        #   Add subfolders to root_folder and append team_view value
        if self.root_folder is None:
            self.root_folder = shared_folder
        else:
            self.root_folder.subfolder.extend(shared_folder.subfolder)
            self.root_folder.team_view += shared_folder.team_view
            # self.folder_hierarchy.team_edit += shared_folder.team_edit

        # Create new folder_mapping for the current folder collection
        self.folder_mapping = {}
        self._map_folders_to_new_ids(shared_folder)

    def get_consolidated_folder_hierarchy(self):
        return self.root_folder

    def get_current_folder_mapping(self):
        return self.folder_mapping

    # Give each folder a new id and content_metadata_id
    def _map_folders_to_new_ids(self, folder: LookerFolder):
        # Increment folder_counter for every new folder recursed through.
        self.folder_counter += 1

        # If Shared Folder, do not add to folder_mapping, rather send each
        # customer folder (e.g. INDCTR, DEMO2) through this method.
        if folder.id == self.SHARED_FOLDER_ID:
            for subfolder in folder.subfolder:
                self._map_folders_to_new_ids(subfolder)
            return

        # If not Shared Folder...

        # ...get new parent_id.
        parent_id = (
            self.folder_mapping[folder.parent_id]["new_id"]
            if folder.parent_id in self.folder_mapping
            else self.SHARED_FOLDER_ID
        )

        # ...store folder info in folder_mapping with new_id set to
        # folder_counter (new_id will be used to update content folder ids
        # later on).
        self.folder_mapping[folder.id] = {
            "name": folder.name,
            "new_id": self.folder_counter,
            "new_parent_id": parent_id,
            "original_parent_id": folder.parent_id,
        }

        # Update folder object with new values (affects
        # self.root_folder/consolidated_folder_hiearchy)
        folder.id = str(self.folder_counter)
        folder.parent_id = str(parent_id)
        folder.content_metadata_id = str(self.folder_counter)

        # ...send each subfolder through this method.
        for subfolder in folder.subfolder:
            self._map_folders_to_new_ids(subfolder)

    def _filter_folders(
        self, folders: list[LookerFolder], customer_folder_ids: list[str] = []
    ):
        filtered_folders = []
        for folder in folders:
            if (
                folder.name in self.customer_include_list
                or folder.parent_id in customer_folder_ids
            ):
                customer_folder_ids.append(folder.id)
                folder.subfolder = self._filter_folders(
                    folder.subfolder, customer_folder_ids
                )
                filtered_folders.append(folder)
        return filtered_folders

    def _filter_folder_access_groups(self, team_view: list[str]):
        return [
            group
            for group in team_view
            if group.split("_")[0] in self.customer_include_list
        ]
