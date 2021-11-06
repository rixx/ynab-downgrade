import collections
import csv
import datetime as dt
import json
import sys
from pathlib import Path


def get_initial_version(path):
    with open(path / "../devices/A.ydevice", "r") as p:
        data = json.load(p)
    return int(data["knowledge"].split("-")[-1])


def write_version(path, version):
    meta_path = path / "../devices/A.ydevice"
    with open(meta_path, "r") as p:
        data = json.load(p)
    data["knowledge"] = f"A-{version}"
    data["knowledgeInFullBudgetFile"] = f"A-{version}"
    with open(meta_path, "w") as p:
        json.dump(data, p, indent="\t", ensure_ascii=False)


def write_budgets(path, budgets):
    with open(path / "Budget.yfull", "r") as p:
        data = json.load(p)

    version = get_initial_version(path) + 1
    # Lookups go name -> obj
    category_lookup = {}
    for mc in data["masterCategories"]:
        for sc in mc["subCategories"]:
            category_lookup[(mc["name"], sc["name"])] = sc

    data_budgets = data["monthlyBudgets"]
    months = sorted(list(budgets.keys()), reverse=True)
    for month in months:
        month_budgets = budgets[month]
        month_id = f"MB/{month}"
        data_month = [d for d in data_budgets if d["entityId"] == month_id]
        if data_month:
            data_month = data_month[0]
            sub_budgets = data_month["monthlySubCategoryBudgets"]
        else:
            version += 1
            data_month = {
                "entityType": "monthlyBudget",
                "monthlySubCategoryBudgets": [],
                "month": f"{month}-01",
                "entityVersion": f"A-{version}",
                "entityId": month_id,
            }
            data_budgets.append(data_month)
        for index, sub_budget in enumerate(month_budgets):
            category_id = category_lookup[
                (sub_budget["Category Group"], sub_budget["Category"])
            ]["entityId"]
            entity_id = f"MCB/{month}/{category_id}"
            data_sub_budget = [
                d
                for d in data_month["monthlySubCategoryBudgets"]
                if d["entityId"] == entity_id
            ]
            if data_sub_budget:
                data_sub_budget = data_sub_budget[0]
                data_sub_budget["budgeted"] = float(sub_budget["Budgeted"][:-1])
            else:
                version += 1
                data_month["monthlySubCategoryBudgets"].append(
                    {
                        "entityType": "monthlyCategoryBudget",
                        "categoryId": category_id,
                        "budgeted": float(sub_budget["Budgeted"][:-1]),
                        "overspendingHandling": None,
                        "entityVersion": f"A-{version}",
                        "entityId": entity_id,
                        "parentMonthlyBudgetId": month_id,
                    }
                )

    data["monthlyBudgets"] = data_budgets
    data["fileMetaData"]["currentKnowledge"] = f"A-{version}"

    with open(path / "Budget.yfull", "w") as p:
        json.dump(data, p, indent="\t", ensure_ascii=False)
    write_version(path, version)


def load_budgets(path):
    """Returns a dict of format {"2016-04": [list of matching lines]}"""
    months = collections.defaultdict(list)
    with open(path) as p:
        data = csv.DictReader(p)
        for line in data:
            month = line.get("Month") or line.get('\ufeff"Month"')
            month = dt.datetime.strptime(month, "%b %Y").strftime("%Y-%m")
            months[month].append(line)
    return months


def main():
    nynab_path = Path(sys.argv[-2])
    ynab4_path = Path(sys.argv[-1])

    for path in (nynab_path, ynab4_path):
        if not path.exists():
            print(f"{path} does not exist!")
            sys.exit(-1)

    budgets = load_budgets(nynab_path)
    write_budgets(ynab4_path, budgets)


if __name__ == "__main__":
    main()
