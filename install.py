import os
folders = [
    "Groceries",
    "Groceries/static",
        "Groceries/static/css"
        "Groceries/static/js"
        "Groceries/static/reports"
        "Groceries/static/uploads"
    "Groceries/templates",
    "Groceries/logs",
    "Groceries/bulk_code",
    "Groceries/code_helpers",
    "Groceries/go_shopping",
    "Groceries/instance",
    "Groceries/logs",
    "Groceries/output",
        "Groceries/output/out_ai",
]

for f in folders:
    os.makedirs(f, exist_ok=True)

