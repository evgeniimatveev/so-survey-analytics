"""Upload app files to HF Space."""
import os
from huggingface_hub import HfApi

TOKEN = os.environ["HF_TOKEN"]
REPO  = "evgeniimatveevusa/so-survey-analytics"

api = HfApi(token=TOKEN)

files = [
    "dashboard/app.py",
    "dashboard/start.sh",
    "src/__init__.py",
    "src/queries.py",
    "scripts/download_db.py",
    "requirements.txt",
    "Dockerfile",
]

for path in files:
    api.upload_file(
        path_or_fileobj=path,
        path_in_repo=path,
        repo_id=REPO,
        repo_type="space",
    )
    print("Uploaded:", path)

print("All files uploaded to HF Space.")
