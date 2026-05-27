"""All analytical SQL queries — 20 business questions."""
import duckdb
import pandas as pd


def _q(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()


# ── Section 1: KPI Row ────────────────────────────────────────────────────────

def kpi_total_responses(conn):
    return _q(conn, "SELECT COUNT(*) AS total FROM survey").iloc[0, 0]

def kpi_median_salary(conn):
    return _q(conn, "SELECT MEDIAN(salary_usd) AS med FROM survey WHERE salary_usd IS NOT NULL").iloc[0, 0]

def kpi_remote_pct(conn):
    return _q(conn, """
        SELECT ROUND(
            COUNT(*) FILTER (WHERE RemoteWork = 'Remote') * 100.0 / COUNT(*), 1
        ) AS pct
        FROM survey WHERE RemoteWork IS NOT NULL
    """).iloc[0, 0]

def kpi_top_language(conn):
    return _q(conn, """
        SELECT lang, cnt FROM (
            SELECT TRIM(lang) AS lang, COUNT(*) AS cnt
            FROM survey, UNNEST(STRING_SPLIT(LanguageHaveWorkedWith, ';')) AS t(lang)
            WHERE LanguageHaveWorkedWith IS NOT NULL
            GROUP BY lang ORDER BY cnt DESC LIMIT 1
        )
    """).iloc[0, 0]


# ── Section 2: Salary Intelligence ───────────────────────────────────────────

def salary_by_language(conn):
    """Q1 — Median salary by programming language (top 15)."""
    return _q(conn, """
        SELECT
            TRIM(lang)                          AS language,
            ROUND(MEDIAN(salary_usd))           AS median_salary,
            COUNT(*)                            AS respondents
        FROM survey, UNNEST(STRING_SPLIT(LanguageHaveWorkedWith, ';')) AS t(lang)
        WHERE salary_usd IS NOT NULL AND LanguageHaveWorkedWith IS NOT NULL
        GROUP BY language
        HAVING COUNT(*) >= 200
        ORDER BY median_salary DESC
        LIMIT 15
    """)

def salary_by_experience(conn):
    """Q2 — Median salary by years of professional experience (bucketed)."""
    return _q(conn, """
        SELECT
            CASE
                WHEN YearsCodePro < 2  THEN '0–1 yrs'
                WHEN YearsCodePro < 5  THEN '2–4 yrs'
                WHEN YearsCodePro < 10 THEN '5–9 yrs'
                WHEN YearsCodePro < 20 THEN '10–19 yrs'
                ELSE '20+ yrs'
            END                             AS exp_bucket,
            ROUND(MEDIAN(salary_usd))       AS median_salary,
            COUNT(*)                        AS respondents
        FROM survey
        WHERE salary_usd IS NOT NULL AND YearsCodePro IS NOT NULL
        GROUP BY exp_bucket
        ORDER BY MEDIAN(salary_usd)
    """)

def salary_by_country(conn):
    """Q3 — Top 15 countries by median developer salary."""
    return _q(conn, """
        SELECT
            Country,
            ROUND(MEDIAN(salary_usd))   AS median_salary,
            COUNT(*)                    AS respondents
        FROM survey
        WHERE salary_usd IS NOT NULL AND Country IS NOT NULL
        GROUP BY Country
        HAVING COUNT(*) >= 100
        ORDER BY median_salary DESC
        LIMIT 15
    """)

def salary_remote_vs_onsite(conn):
    """Q4 — Remote vs hybrid vs on-site salary comparison."""
    return _q(conn, """
        SELECT
            RemoteWork,
            ROUND(MEDIAN(salary_usd))   AS median_salary,
            ROUND(AVG(salary_usd))      AS mean_salary,
            COUNT(*)                    AS respondents
        FROM survey
        WHERE salary_usd IS NOT NULL AND RemoteWork IS NOT NULL
        GROUP BY RemoteWork
        ORDER BY median_salary DESC
    """)

def salary_by_org_size(conn):
    """Q5 — Salary by company size."""
    return _q(conn, """
        SELECT
            OrgSize,
            ROUND(MEDIAN(salary_usd))   AS median_salary,
            COUNT(*)                    AS respondents
        FROM survey
        WHERE salary_usd IS NOT NULL AND OrgSize IS NOT NULL
        GROUP BY OrgSize
        ORDER BY median_salary DESC
    """)


# ── Section 3: Tech Stack Rankings ───────────────────────────────────────────

def top_languages(conn):
    """Q6 — Most used programming languages."""
    return _q(conn, """
        SELECT TRIM(lang) AS language, COUNT(*) AS users
        FROM survey, UNNEST(STRING_SPLIT(LanguageHaveWorkedWith, ';')) AS t(lang)
        WHERE LanguageHaveWorkedWith IS NOT NULL
        GROUP BY language
        ORDER BY users DESC
        LIMIT 15
    """)

def top_databases(conn):
    """Q7 — Most used databases."""
    return _q(conn, """
        SELECT TRIM(db) AS database_name, COUNT(*) AS users
        FROM survey, UNNEST(STRING_SPLIT(DatabaseHaveWorkedWith, ';')) AS t(db)
        WHERE DatabaseHaveWorkedWith IS NOT NULL
        GROUP BY database_name
        ORDER BY users DESC
        LIMIT 12
    """)

def top_cloud_platforms(conn):
    """Q8 — Most used cloud platforms."""
    return _q(conn, """
        SELECT TRIM(platform) AS cloud_platform, COUNT(*) AS users
        FROM survey, UNNEST(STRING_SPLIT(PlatformHaveWorkedWith, ';')) AS t(platform)
        WHERE PlatformHaveWorkedWith IS NOT NULL
        GROUP BY cloud_platform
        ORDER BY users DESC
        LIMIT 10
    """)

def language_salary_heatmap(conn):
    """Q9 — Top 10 languages × experience bucket salary grid."""
    return _q(conn, """
        WITH base AS (
            SELECT
                TRIM(lang) AS language,
                CASE
                    WHEN YearsCodePro < 2  THEN '0–1y'
                    WHEN YearsCodePro < 5  THEN '2–4y'
                    WHEN YearsCodePro < 10 THEN '5–9y'
                    ELSE '10y+'
                END AS exp_bucket,
                salary_usd
            FROM survey, UNNEST(STRING_SPLIT(LanguageHaveWorkedWith, ';')) AS t(lang)
            WHERE salary_usd IS NOT NULL AND YearsCodePro IS NOT NULL
              AND LanguageHaveWorkedWith IS NOT NULL
        ),
        top_langs AS (
            SELECT language FROM base GROUP BY language
            HAVING COUNT(*) >= 300 ORDER BY COUNT(*) DESC LIMIT 10
        )
        SELECT b.language, b.exp_bucket, ROUND(MEDIAN(b.salary_usd)) AS median_salary
        FROM base b JOIN top_langs tl ON b.language = tl.language
        GROUP BY b.language, b.exp_bucket
        ORDER BY b.language, b.exp_bucket
    """)


# ── Section 4: Remote Work ────────────────────────────────────────────────────

def remote_by_country(conn):
    """Q10 — % fully remote by country (top 15 by volume)."""
    return _q(conn, """
        WITH base AS (
            SELECT Country,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE RemoteWork = 'Remote') AS remote_count
            FROM survey
            WHERE Country IS NOT NULL AND RemoteWork IS NOT NULL
            GROUP BY Country
            HAVING COUNT(*) >= 100
        )
        SELECT Country,
               ROUND(remote_count * 100.0 / total, 1) AS remote_pct,
               total AS respondents
        FROM base
        ORDER BY remote_pct DESC
        LIMIT 15
    """)

def remote_by_experience(conn):
    """Q11 — Remote work rate by experience level."""
    return _q(conn, """
        SELECT
            CASE
                WHEN YearsCodePro < 2  THEN '0–1 yrs'
                WHEN YearsCodePro < 5  THEN '2–4 yrs'
                WHEN YearsCodePro < 10 THEN '5–9 yrs'
                WHEN YearsCodePro < 20 THEN '10–19 yrs'
                ELSE '20+ yrs'
            END AS exp_bucket,
            ROUND(
                COUNT(*) FILTER (WHERE RemoteWork = 'Remote') * 100.0 / COUNT(*), 1
            ) AS remote_pct,
            COUNT(*) AS respondents
        FROM survey
        WHERE RemoteWork IS NOT NULL AND YearsCodePro IS NOT NULL
        GROUP BY exp_bucket
        ORDER BY MEDIAN(YearsCodePro)
    """)

def remote_distribution(conn):
    """Q12 — Remote / Hybrid / In-person split overall."""
    return _q(conn, """
        SELECT RemoteWork, COUNT(*) AS respondents,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM survey
        WHERE RemoteWork IS NOT NULL
        GROUP BY RemoteWork
        ORDER BY respondents DESC
    """)


# ── Section 5: Developer Profile ─────────────────────────────────────────────

def experience_distribution(conn):
    """Q13 — Distribution of professional coding experience."""
    return _q(conn, """
        SELECT
            CASE
                WHEN YearsCodePro < 2  THEN '0–1 yrs'
                WHEN YearsCodePro < 5  THEN '2–4 yrs'
                WHEN YearsCodePro < 10 THEN '5–9 yrs'
                WHEN YearsCodePro < 20 THEN '10–19 yrs'
                ELSE '20+ yrs'
            END AS exp_bucket,
            COUNT(*) AS respondents
        FROM survey WHERE YearsCodePro IS NOT NULL
        GROUP BY exp_bucket
        ORDER BY MEDIAN(YearsCodePro)
    """)

def education_vs_salary(conn):
    """Q14 — Does education level matter for salary?"""
    return _q(conn, """
        SELECT
            EdLevel,
            ROUND(MEDIAN(salary_usd)) AS median_salary,
            COUNT(*) AS respondents
        FROM survey
        WHERE salary_usd IS NOT NULL AND EdLevel IS NOT NULL
        GROUP BY EdLevel
        HAVING COUNT(*) >= 100
        ORDER BY median_salary DESC
    """)

def top_countries_by_volume(conn):
    """Q15 — Countries with most survey respondents."""
    return _q(conn, """
        SELECT Country, COUNT(*) AS respondents
        FROM survey WHERE Country IS NOT NULL
        GROUP BY Country
        ORDER BY respondents DESC
        LIMIT 15
    """)

def employment_type(conn):
    """Q16 — Employment type breakdown."""
    return _q(conn, """
        SELECT Employment, COUNT(*) AS respondents,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM survey WHERE Employment IS NOT NULL
        GROUP BY Employment
        ORDER BY respondents DESC
        LIMIT 8
    """)


# ── Section 6: DA / DE Focus ──────────────────────────────────────────────────

def data_roles_salary(conn):
    """Q17 — Median salary for Data Analyst / Data Engineer / Data Scientist."""
    return _q(conn, """
        SELECT
            TRIM(role) AS dev_type,
            ROUND(MEDIAN(salary_usd)) AS median_salary,
            COUNT(*) AS respondents
        FROM survey, UNNEST(STRING_SPLIT(DevType, ';')) AS t(role)
        WHERE salary_usd IS NOT NULL AND DevType IS NOT NULL
          AND (LOWER(role) LIKE '%data%' OR LOWER(role) LIKE '%analyst%'
               OR LOWER(role) LIKE '%scientist%' OR LOWER(role) LIKE '%engineer%')
        GROUP BY dev_type
        HAVING COUNT(*) >= 50
        ORDER BY median_salary DESC
        LIMIT 12
    """)

def sql_usage_rate(conn):
    """Q18 — What % of data professionals use SQL?"""
    return _q(conn, """
        WITH data_folks AS (
            SELECT ResponseId, LanguageHaveWorkedWith
            FROM survey, UNNEST(STRING_SPLIT(DevType, ';')) AS t(role)
            WHERE LOWER(role) LIKE '%data%' AND DevType IS NOT NULL
        )
        SELECT
            COUNT(*) AS total_data_pros,
            COUNT(*) FILTER (
                WHERE LanguageHaveWorkedWith LIKE '%SQL%'
            ) AS use_sql,
            ROUND(
                COUNT(*) FILTER (WHERE LanguageHaveWorkedWith LIKE '%SQL%')
                * 100.0 / COUNT(*), 1
            ) AS sql_pct
        FROM data_folks
    """)

def python_vs_r_data(conn):
    """Q19 — Python vs R adoption among data professionals."""
    return _q(conn, """
        WITH data_folks AS (
            SELECT ResponseId, LanguageHaveWorkedWith
            FROM survey, UNNEST(STRING_SPLIT(DevType, ';')) AS t(role)
            WHERE LOWER(role) LIKE '%data%' AND DevType IS NOT NULL
              AND LanguageHaveWorkedWith IS NOT NULL
        )
        SELECT
            'Python' AS language,
            COUNT(*) FILTER (WHERE LanguageHaveWorkedWith LIKE '%Python%') AS users,
            ROUND(COUNT(*) FILTER (WHERE LanguageHaveWorkedWith LIKE '%Python%')
                  * 100.0 / COUNT(*), 1) AS adoption_pct
        FROM data_folks
        UNION ALL
        SELECT
            'R' AS language,
            COUNT(*) FILTER (WHERE LanguageHaveWorkedWith LIKE '%R;%'
                              OR LanguageHaveWorkedWith LIKE '%R'
                              OR LanguageHaveWorkedWith = 'R') AS users,
            ROUND(COUNT(*) FILTER (WHERE LanguageHaveWorkedWith LIKE '%R;%'
                                    OR LanguageHaveWorkedWith LIKE '%R'
                                    OR LanguageHaveWorkedWith = 'R')
                  * 100.0 / COUNT(*), 1) AS adoption_pct
        FROM data_folks
    """)

def ai_tool_adoption(conn):
    """Q20 — AI tool adoption: are devs using AI in their workflow?"""
    return _q(conn, """
        SELECT
            AISelect,
            COUNT(*) AS respondents,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM survey WHERE AISelect IS NOT NULL
        GROUP BY AISelect
        ORDER BY respondents DESC
    """)
