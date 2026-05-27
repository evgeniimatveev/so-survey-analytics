"""Upload survey.duckdb to HuggingFace Dataset."""
import os
from pathlib import Path
from huggingface_hub import HfApi

TOKEN = os.environ["HF_TOKEN"]
REPO  = "evgeniimatveevusa/so-survey-db"
DB    = Path("data/survey.duckdb")

api = HfApi(token=TOKEN)
api.create_repo(repo_id=REPO, repo_type="dataset", exist_ok=True)
api.upload_file(
    path_or_fileobj=str(DB),
    path_in_repo="survey.duckdb",
    repo_id=REPO,
    repo_type="dataset",
)
print(f"Uploaded {DB} → hf://datasets/{REPO}/survey.duckdb")
