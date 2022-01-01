import collections
import csv
import json
import sys
import uuid
from pathlib import Path


def get_initial_version(path):
    with open(path / "../devices/A.ydevice", "r", encoding="utf-8-sig") as p:
        data = json.load(p)
    return int(data["knowledge"].split("-")[-1])


def write_version(path, version):
    meta_path = path / "../devices/A.ydevice"
    with open(meta_path, "r", encoding="utf-8-sig") as p:
        data = json.load(p)
    data["knowledge"] = f"A-{version}"
    data["knowledgeInFullBudgetFile"] = f"A-{version}"
    with open(meta_path, "w", encoding="utf-8-sig") as p:
        json.dump(data, p, indent="\t")


def write_categories(path, categories):
    """
    Here, we completely replace the masterCategories part of the Budget.yfull
    """
    version = get_initial_version(path) + 1
    new_categories = []
    for index, (category, sub_categories) in enumerate(categories.items()):
        category_id = str(uuid.uuid4()).upper()  # A2
        category_data = {
            "entityType": "masterCategory",
            "expanded": True,
            "name": category,
            "type": "OUTFLOW",
            "deleteable": True,
            "subCategories": [
                {
                    "entityType": "category",
                    "name": sub_category,
                    "type": "OUTFLOW",
                    "cachedBalance": 0,
                    "masterCategoryId": category_id,
                    "entityVersion": f"A-{version + inner_index}",
                    "entityId": str(uuid.uuid4()).upper(),
                    "sortableIndex": inner_index * 10000000,
                }
                for inner_index, sub_category in enumerate(sub_categories)
            ],
            "entityVersion": f"A-{version + len(sub_categories)}",
            "entityId": category_id,
            "sortableIndex": index * 10000000,
        }
        if category == "Hidden Categories":
            category_data["name"] = "Imported Hidden Categories"
        new_categories.append(category_data)
        version += len(sub_categories) + 1

    with open(path / "Budget.yfull", "r", encoding="utf-8-sig") as p:
        data = json.load(p)

    data["masterCategories"] = [data["masterCategories"][0]] + new_categories
    # Keep hidden categories, too hard to sync
    # due to super weird cat name syntax.
    # Let's just assume that they are always first

    data["fileMetaData"]["currentKnowledge"] = f"A-{version}"

    with open(path / "Budget.yfull", "w", encoding="utf-8-sig") as p:
        json.dump(data, p, indent="\t")

    write_version(path, version)


def load_categories(path):
    categories = collections.defaultdict(set)
    with open(path, encoding="utf-8-sig") as p:
        data = csv.DictReader(p)
        for line in data:
            categories[line["Category Group"]].add(line["Category"])
    return categories


def main():
    nynab_path = Path(sys.argv[-2])
    ynab4_path = Path(sys.argv[-1])

    for path in (nynab_path, ynab4_path):
        if not path.exists():
            print(f"{path} does not exist!")
            sys.exit(-1)

    categories = load_categories(nynab_path)
    write_categories(ynab4_path, categories)


if __name__ == "__main__":
    main()
