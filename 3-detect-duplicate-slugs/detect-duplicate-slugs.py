import yaml
import os
from collections import defaultdict


class DashboardObject:
    """Represents a dashboard object with a slug."""

    def __init__(self, dashboard_slug):
        self.dashboard_slug = dashboard_slug

    def __repr__(self):
        return f"DashboardObject(dashboard_slug={self.dashboard_slug})"


# Constructor for !DashboardObject
def dashboard_object_constructor(loader, node):
    data = loader.construct_mapping(node)
    dashboard_slug = data.get("dashboard_slug", None)
    return DashboardObject(dashboard_slug)


# Dummy constructor for !LookObject and !ScheduledPlan (to avoid errors)
def dummy_constructor(loader, node):
    return None


def find_content_files(directory):
    filename = "content.yaml"
    matches = []
    for root, dirs, files in os.walk(directory):
        if filename in files:
            relative_path = os.path.relpath(root, directory)
            matches.append(os.path.join(relative_path, filename))
    return matches


def get_dashboard_slugs(path: str):
    dashboard_slugs = defaultdict(list)
    files = find_content_files(path)

    for filename in files:
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(path, filename)

            with open(filepath, "r") as file:
                yaml_objects = yaml.load(file, Loader=yaml.FullLoader)

                if not yaml_objects:
                    continue

                dashboard_slugs[filename] = [
                    o.dashboard_slug
                    for o in yaml_objects
                    if isinstance(o, DashboardObject)
                ]

    return dashboard_slugs


def find_duplicates(dashboard_slugs):
    slug_counts = {}

    for filename in dashboard_slugs:
        slugs = dashboard_slugs[filename]

        for slug in slugs:
            if slug in slug_counts:
                count = slug_counts[slug]["count"]
                occurences = slug_counts[slug]["occurences"]
                slug_counts[slug] = {
                    "occurences": occurences + [filename],
                    "count": count + 1,
                }
            else:
                slug_counts[slug] = {"occurences": [filename], "count": 1}

    return slug_counts


# Register constructors
yaml.add_constructor("!DashboardObject", dashboard_object_constructor)
yaml.add_constructor("!LookObject", dummy_constructor)
yaml.add_constructor("!ScheduledPlan", dummy_constructor)
yaml.add_constructor("!AlertObject", dummy_constructor)

# Find duplicate slugs
path = "../2-lmanage-capturator/config"
dashboard_slugs = get_dashboard_slugs(path)
slug_counts = find_duplicates(dashboard_slugs)
dupe_found = False

for slug in slug_counts:
    s = slug_counts[slug]
    if s["count"] > 1:
        dupe_found = True
        print(f"Duplicate dashboard slug {slug} detected in {s['occurences']}")

if not dupe_found:
    print("No duplicate dashboard slugs found.")
