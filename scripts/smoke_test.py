"""Smoke tests — verify all 20 SQL queries return non-empty results."""
import sys
sys.path.insert(0, ".")
import duckdb
from src import queries as q

DB = "data/survey.duckdb"
PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"

conn = duckdb.connect(DB, read_only=True)
failures = []

checks = [
    ("kpi_total_responses",   lambda: q.kpi_total_responses(conn) > 0),
    ("kpi_median_salary",     lambda: q.kpi_median_salary(conn) > 0),
    ("kpi_remote_pct",        lambda: q.kpi_remote_pct(conn) > 0),
    ("kpi_top_language",      lambda: len(q.kpi_top_language(conn)) > 0),
    ("salary_by_language",    lambda: len(q.salary_by_language(conn)) >= 10),
    ("salary_by_experience",  lambda: len(q.salary_by_experience(conn)) == 5),
    ("salary_by_country",     lambda: len(q.salary_by_country(conn)) >= 10),
    ("salary_remote_onsite",  lambda: len(q.salary_remote_vs_onsite(conn)) == 3),
    ("salary_by_org_size",    lambda: len(q.salary_by_org_size(conn)) >= 3),
    ("top_languages",         lambda: len(q.top_languages(conn)) == 15),
    ("top_databases",         lambda: len(q.top_databases(conn)) >= 8),
    ("top_cloud_platforms",   lambda: len(q.top_cloud_platforms(conn)) >= 5),
    ("language_salary_hmap",  lambda: len(q.language_salary_heatmap(conn)) > 0),
    ("remote_by_country",     lambda: len(q.remote_by_country(conn)) >= 10),
    ("remote_by_experience",  lambda: len(q.remote_by_experience(conn)) == 5),
    ("remote_distribution",   lambda: len(q.remote_distribution(conn)) == 3),
    ("experience_dist",       lambda: len(q.experience_distribution(conn)) == 5),
    ("education_vs_salary",   lambda: len(q.education_vs_salary(conn)) >= 5),
    ("top_countries_volume",  lambda: len(q.top_countries_by_volume(conn)) == 15),
    ("data_roles_salary",     lambda: len(q.data_roles_salary(conn)) >= 5),
    ("sql_usage_rate",        lambda: float(q.sql_usage_rate(conn)["sql_pct"].iloc[0]) > 0),
    ("python_vs_r",           lambda: len(q.python_vs_r_data(conn)) == 2),
    ("ai_tool_adoption",      lambda: len(q.ai_tool_adoption(conn)) >= 2),
]

for name, check in checks:
    try:
        ok = check()
        print(f"{PASS if ok else FAIL}  {name}")
        if not ok:
            failures.append(name)
    except Exception as e:
        print(f"{FAIL}  {name}  — {e}")
        failures.append(name)

conn.close()
print(f"\n{len(checks) - len(failures)}/{len(checks)} checks passed")

if failures:
    print("FAILED:", failures)
    sys.exit(1)
