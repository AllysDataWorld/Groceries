import re

def clean_requirements(path="requirements.txt"):
    # Regex patterns that indicate Windows-specific entries
    windows_patterns = [
        r"file:///C:/",   # pip local wheel paths
        r"C:\\",          # Windows absolute paths
        r"C:/",           # Windows absolute paths
    ]

    cleaned_lines = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Skip lines that match any Windows pattern
            if any(re.search(p, stripped) for p in windows_patterns):
                print(f"Removing Windows-specific entry: {stripped}")
                continue

            cleaned_lines.append(stripped)

    # Write cleaned requirements back
    with open(path, "w", encoding="utf-8") as f:
        for line in cleaned_lines:
            f.write(line + "\n")

    print("requirements.txt cleaned successfully!")

# import os
# folders = [
#     "Groceries",
#     "Groceries/static",
#         "Groceries/static/css"
#         "Groceries/static/js"
#         "Groceries/static/reports"
#         "Groceries/static/uploads"
#     "Groceries/templates",
#     "Groceries/logs",
#     "Groceries/bulk_code",
#     "Groceries/code_helpers",
#     "Groceries/go_shopping",
#     "Groceries/instance",
#     "Groceries/logs",
#     "Groceries/output",
#         "Groceries/output/out_ai",
# ]
#
# for f in folders:
#     os.makedirs(f, exist_ok=True)

