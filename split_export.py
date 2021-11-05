import collections
import csv
import sys
from pathlib import Path


def main():
    nynab_path = Path(sys.argv[-1])
    if not nynab_path.exists():
        print(f"{nynab_path} does not exist!")
        sys.exit(-1)

    with open(nynab_path, "r") as p:
        content = list(csv.DictReader(p))

    result = collections.defaultdict(list)
    for line in content:
        # Thanks for these replacements go to /u/loftyDan
        # https://www.reddit.com/r/ynab/comments/qlglh3/importing_data_from_nynab_to_ynab4/hj8dhwu/
        line["Master Category"] = line.pop("Category Group").replace("Inflow", "Income")
        line["Sub Category"] = line.pop("Category").replace(
            "Ready to Assign", "Available this month"
        )
        line["Category"] = line.pop("Category Group/Category").replace(
            "Inflow: Ready to Assign", "Income: Available this month"
        )
        account = line.get('\ufeff"Account"') or line.get("Account")
        result[account].append(line)

    for account, lines in result.items():
        with open(f"ynab_split_{account}.csv", "w") as p:
            writer = csv.DictWriter(
                p,
                fieldnames=[
                    '\ufeff"Account"',
                    "Flag",
                    "Date",
                    "Payee",
                    "Category",
                    "Master Category",
                    "Sub Category",
                    "Memo",
                    "Outflow",
                    "Inflow",
                    "Cleared",
                ],
            )
            writer.writeheader()
            writer.writerows(lines)


if __name__ == "__main__":
    main()
