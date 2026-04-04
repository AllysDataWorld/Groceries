import re

import re

def clean_requirements(path="requirements.txt", output="requirements_clean.txt"):
    # Patterns that indicate invalid or platform-specific entries
    bad_patterns = [
        r"file:///C:/",
        r"C:\\",
        r"C:/",
        r"file:///opt/conda/",
        r"file:///croot/",
        r"/croot/",
        r"/opt/conda/",
        r"@ file://",        # any local file reference
        r"\.whl",            # local wheel paths
    ]

    # Windows-only packages to remove entirely
    windows_only = [
        "pywin32",
        "pywinpty",
        "pywin32-ctypes",
        "winloop",
        "win-inet-pton",
    ]

    cleaned = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            if not stripped:
                continue

            # Remove Windows-only packages
            if any(stripped.lower().startswith(pkg) for pkg in windows_only):
                print(f"Removing Windows-only package: {stripped}")
                continue

            # Remove lines containing invalid paths
            if any(re.search(p, stripped) for p in bad_patterns):
                print(f"Removing invalid entry: {stripped}")
                continue

            # Keep the line
            cleaned.append(stripped)

    # Write cleaned file
    with open(output, "w", encoding="utf-8") as f:
        for line in cleaned:
            f.write(line + "\n")

    print(f"Cleaned requirements written to {output}")

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

