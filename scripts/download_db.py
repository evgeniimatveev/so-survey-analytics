"""Download survey.duckdb from HuggingFace Dataset (used by HF Space on startup)."""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

REPO   = "evgeniimatveevusa/so-survey-db"
DB_OUT = Path("data/survey.duckdb")

DB_OUT.parent.mkdir(exist_ok=True)
path = hf_hub_download(
    repo_id=REPO,
    filename="survey.duckdb",
    repo_type="dataset",
    local_dir=str(DB_OUT.parent),
    token=os.environ.get("HF_TOKEN"),
)
print(f"Downloaded → {path}")
