import os

# Check if we're running in a headless environment (like GitHub Actions)
HEADLESS = (
    os.environ.get("CI") == "true"
    or os.environ.get("GITHUB_ACTIONS") == "true"
    or os.environ.get("HEADLESS", "").lower() in ("true", "1", "yes")
)

print(f"CI: {os.environ.get('CI')}")
print(f"GITHUB_ACTIONS: {os.environ.get('GITHUB_ACTIONS')}")
print(f"HEADLESS: {os.environ.get('HEADLESS')}")
print(f"HEADLESS.lower(): {os.environ.get('HEADLESS', '').lower()}")
print(f"Final HEADLESS value: {HEADLESS}")
