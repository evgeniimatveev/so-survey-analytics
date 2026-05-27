"""Load Stack Overflow Survey CSV into DuckDB."""
import duckdb
import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/survey_results_public.csv")
DB_PATH  = Path("data/survey.duckdb")

KEEP_COLS = [
    "ResponseId",
    "MainBranch",
    "Age",
    "Employment",
    "RemoteWork",
    "EdLevel",
    "YearsCode",
    "YearsCodePro",
    "DevType",
    "OrgSize",
    "Country",
    "ConvertedCompYearly",
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith",
    "PlatformHaveWorkedWith",
    "WebframeHaveWorkedWith",
    "MiscTechHaveWorkedWith",
    "AISelect",
    "JobSat",
    "Industry",
]


def load():
    print(f"Reading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, usecols=lambda c: c in KEEP_COLS, low_memory=False)
    print(f"  Rows: {len(df):,}  Cols: {len(df.columns)}")

    # Salary: keep only USD-plausible range ($10k – $2M)
    if "ConvertedCompYearly" in df.columns:
        df["salary_usd"] = pd.to_numeric(df["ConvertedCompYearly"], errors="coerce")
        df = df.drop(columns=["ConvertedCompYearly"])
        before = len(df)
        df = df[(df["salary_usd"].isna()) | ((df["salary_usd"] >= 10_000) & (df["salary_usd"] <= 2_000_000))]
        print(f"  Salary outliers removed: {before - len(df):,}")

    # Numeric experience columns
    for col in ("YearsCode", "YearsCodePro"):
        if col in df.columns:
            df[col] = df[col].replace({"Less than 1 year": "0", "More than 50 years": "51"})
            df[col] = pd.to_numeric(df[col], errors="coerce")

    DB_PATH.parent.mkdir(exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("DROP TABLE IF EXISTS survey")
    conn.execute("CREATE TABLE survey AS SELECT * FROM df")
    count = conn.execute("SELECT COUNT(*) FROM survey").fetchone()[0]
    conn.close()
    print(f"  Saved to {DB_PATH}  ({count:,} rows)")


if __name__ == "__main__":
    load()
