import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import queries as q

DB_PATH = Path("data/survey.duckdb")

st.set_page_config(
    page_title="SO Survey Analytics 2024",
    page_icon="📊",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #1a0533, #2d1b69, #1e3a5f);
    border-radius: 16px;
    padding: 2rem 2.5rem 1.5rem;
    margin-bottom: 1.5rem;
}
.hero h1 { font-size: 2.4rem; font-weight: 800; color: #fff; margin: 0 0 0.3rem 0; letter-spacing: -1px; }
.hero p  { color: #94a3b8; font-size: 1rem; margin: 0; }
.hero .badge {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    border: 1px solid #8b5cf6;
    color: #a78bfa;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    margin-top: 0.7rem;
    font-weight: 600;
}
.kpi-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.kpi-card:hover { border-color: #8b5cf6; }
.kpi-label { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
.kpi-icon  { font-size: 1.4rem; margin-bottom: 0.3rem; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #f1f5f9; line-height: 1.1; }
.kpi-sub   { font-size: 0.78rem; color: #a78bfa; margin-top: 0.25rem; font-weight: 500; }
.section-title { font-size: 1.25rem; font-weight: 700; color: #e2e8f0; margin: 0.5rem 0 0.2rem 0; }
.section-sub   { color: #64748b; font-size: 0.85rem; margin-bottom: 1rem; }
.custom-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, #334155, transparent); margin: 1.5rem 0; }
.insight-box {
    background: rgba(139,92,246,0.08);
    border-left: 3px solid #8b5cf6;
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0 1rem 0;
    color: #cbd5e1;
    font-size: 0.88rem;
}
.findings-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
}
.finding-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    position: relative;
}
.finding-card:hover { border-color: #8b5cf6; }
.finding-num {
    font-size: 2rem;
    font-weight: 900;
    color: rgba(139,92,246,0.25);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.finding-stat {
    font-size: 1.6rem;
    font-weight: 800;
    color: #a78bfa;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}
.finding-text {
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.4;
}
.finding-tag {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    color: #a78bfa;
    border-radius: 4px;
    padding: 0.1rem 0.5rem;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return duckdb.connect(str(DB_PATH), read_only=True)

@st.cache_data(ttl=86400)
def cached(fn_name: str):
    conn = get_conn()
    return getattr(q, fn_name)(conn)

conn = get_conn()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📊 Stack Overflow Developer Survey 2024</h1>
    <p>65,000+ developers · salaries · remote work · tech stacks · what the data actually says</p>
    <span class="badge">📅 Annual Survey · May 2024 · 185 Countries</span>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
total    = q.kpi_total_responses(conn)
med_sal  = q.kpi_median_salary(conn)
rem_pct  = q.kpi_remote_pct(conn)
top_lang = q.kpi_top_language(conn)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">👥</div>
    <div class="kpi-label">Respondents</div>
    <div class="kpi-value">{total:,}</div>
    <div class="kpi-sub">185 countries</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">💰</div>
    <div class="kpi-label">Median Salary</div>
    <div class="kpi-value">${med_sal:,.0f}</div>
    <div class="kpi-sub">USD · annual · filtered</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🌐</div>
    <div class="kpi-label">Fully Remote</div>
    <div class="kpi-value">{rem_pct}%</div>
    <div class="kpi-sub">of employed devs</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🏆</div>
    <div class="kpi-label">Most Used Language</div>
    <div class="kpi-value">{top_lang}</div>
    <div class="kpi-sub">by respondent count</div></div>""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Key Findings ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Key Findings</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">What 65,000 developers tell us about the state of tech in 2024</div>', unsafe_allow_html=True)

# Compute findings dynamically from data
_rem_sal  = q.salary_remote_vs_onsite(conn)
_rem_row  = _rem_sal[_rem_sal["RemoteWork"] == "Remote"]
_onsite   = _rem_sal[_rem_sal["RemoteWork"] == "In-person"]
_rem_med  = int(_rem_row["median_salary"].iloc[0]) if not _rem_row.empty else 0
_on_med   = int(_onsite["median_salary"].iloc[0]) if not _onsite.empty else 1
_rem_prem = round((_rem_med - _on_med) / _on_med * 100, 1)

_sql_df   = q.sql_usage_rate(conn)
_sql_pct  = float(_sql_df["sql_pct"].iloc[0])

_py_r     = q.python_vs_r_data(conn)
_py_pct   = float(_py_r[_py_r["language"] == "Python"]["adoption_pct"].iloc[0])
_r_pct    = float(_py_r[_py_r["language"] == "R"]["adoption_pct"].iloc[0])

_exp_rem  = q.remote_by_experience(conn)
_senior   = _exp_rem[_exp_rem["exp_bucket"] == "20+ yrs"]["remote_pct"].iloc[0]
_junior   = _exp_rem[_exp_rem["exp_bucket"] == "0–1 yrs"]["remote_pct"].iloc[0]

st.markdown(f"""
<div class="findings-grid">

  <div class="finding-card">
    <div class="finding-tag">Salary</div>
    <div class="finding-stat">+{_rem_prem}%</div>
    <div class="finding-text">Remote developers earn <b>{_rem_prem}% more</b> than in-person on median salary — working from home pays off.</div>
  </div>

  <div class="finding-card">
    <div class="finding-tag">Skills</div>
    <div class="finding-stat">{_sql_pct:.0f}%</div>
    <div class="finding-text">of data professionals use <b>SQL</b> — the single most universal skill across every data role, from analyst to engineer.</div>
  </div>

  <div class="finding-card">
    <div class="finding-tag">Languages</div>
    <div class="finding-stat">Python wins</div>
    <div class="finding-text"><b>{_py_pct:.0f}% Python</b> vs <b>{_r_pct:.0f}% R</b> among data professionals. Python won the data language war — by a landslide.</div>
  </div>

  <div class="finding-card">
    <div class="finding-tag">Remote</div>
    <div class="finding-stat">42.5%</div>
    <div class="finding-text"><b>Hybrid is the new normal</b> — only 19.6% are fully in-person. The office-only era is over for most tech companies.</div>
  </div>

  <div class="finding-card">
    <div class="finding-tag">Experience</div>
    <div class="finding-stat">{_senior:.0f}% vs {_junior:.0f}%</div>
    <div class="finding-text">Senior devs (20+ yrs) go remote at <b>{_senior:.0f}%</b> vs only <b>{_junior:.0f}%</b> for juniors — experience buys flexibility.</div>
  </div>

  <div class="finding-card">
    <div class="finding-tag">Databases</div>
    <div class="finding-stat">PostgreSQL #1</div>
    <div class="finding-text"><b>PostgreSQL overtook MySQL</b> as the most-used database — the open-source shift in enterprise data is real and accelerating.</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 2: Salary Intelligence ───────────────────────────────────────────
st.markdown('<div class="section-title">💰 Salary Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Median annual salary (USD) — filtered $10K–$2M · 21,000+ valid responses</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["By Language", "By Experience", "By Country", "Remote vs On-site"])

with tab1:
    df = cached("salary_by_language")
    fig = go.Figure(go.Bar(
        x=df["median_salary"], y=df["language"], orientation="h",
        marker_color="#8b5cf6",
        text=df["median_salary"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="outside", textfont=dict(size=11, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>Median: $%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=480, margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor="#1e293b", tickformat="$,.0f", color="#64748b"),
        yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=12)),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">💡 Erlang, Clojure and Elixir pay highest — niche languages command premium. Among mainstream: Go, Swift and Kotlin lead over Python and JavaScript.</div>', unsafe_allow_html=True)

with tab2:
    df = cached("salary_by_experience")
    order = ["0–1 yrs", "2–4 yrs", "5–9 yrs", "10–19 yrs", "20+ yrs"]
    df["exp_bucket"] = pd.Categorical(df["exp_bucket"], categories=order, ordered=True)
    df = df.sort_values("exp_bucket")
    fig = go.Figure(go.Bar(
        x=df["exp_bucket"], y=df["median_salary"],
        marker_color=["#334155", "#4c1d95", "#6d28d9", "#8b5cf6", "#a78bfa"],
        text=df["median_salary"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="outside", textfont=dict(size=12, color="#94a3b8"),
        hovertemplate="<b>%{x}</b><br>Median: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(showgrid=False, color="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", tickformat="$,.0f", color="#64748b"),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">💡 Salary more than doubles from entry level to 10+ years. The steepest jump happens between 2–4 and 5–9 years — mid-level is where pay accelerates fastest.</div>', unsafe_allow_html=True)

with tab3:
    df = cached("salary_by_country")
    fig = go.Figure(go.Bar(
        x=df["median_salary"], y=df["Country"], orientation="h",
        marker_color="#6d28d9",
        text=df["median_salary"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="outside", textfont=dict(size=11, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>Median: $%{x:,.0f}<br>Respondents: %{customdata:,}<extra></extra>",
        customdata=df["respondents"],
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=480, margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor="#1e293b", tickformat="$,.0f", color="#64748b"),
        yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=12)),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">💡 US leads by a wide margin. Switzerland, Australia and Israel cluster in the $90k+ range. Eastern Europe and Asia show $20k–$40k median — massive geographic pay gap for the same skills.</div>', unsafe_allow_html=True)

with tab4:
    df = cached("salary_remote_vs_onsite")
    colors = {"Remote": "#8b5cf6", "Hybrid (some remote, some in-person)": "#6d28d9", "In-person": "#334155"}
    df["color"] = df["RemoteWork"].map(colors).fillna("#475569")
    fig = go.Figure(go.Bar(
        x=df["RemoteWork"], y=df["median_salary"],
        marker_color=df["color"].tolist(),
        text=df["median_salary"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="outside", textfont=dict(size=13, color="#94a3b8"),
        hovertemplate="<b>%{x}</b><br>Median: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=360, margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(showgrid=False, color="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", tickformat="$,.0f", color="#64748b"),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 3: Tech Stack Rankings ───────────────────────────────────────────
st.markdown('<div class="section-title">🛠️ Tech Stack Rankings</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Most used technologies among 65,000+ developers worldwide</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    st.markdown("**Top 15 Programming Languages**")
    df = cached("top_languages")
    LANG_COLORS = {
        "JavaScript": "#f7df1e", "Python": "#3776ab", "TypeScript": "#3178c6",
        "HTML/CSS": "#e34f26", "SQL": "#e38c00", "Bash/Shell": "#4eaa25",
        "Java": "#ed8b00", "C#": "#239120", "C++": "#00599c", "Go": "#00add8",
        "Rust": "#dea584", "Kotlin": "#7f52ff", "PHP": "#777bb4",
        "PowerShell": "#012456", "Ruby": "#cc342d",
    }
    df["color"] = df["language"].map(LANG_COLORS).fillna("#64748b")
    fig = go.Figure(go.Bar(
        x=df["users"], y=df["language"], orientation="h",
        marker_color=df["color"].tolist(),
        text=df["users"].apply(lambda v: f"{v/1000:.1f}k"),
        textposition="outside", textfont=dict(size=10, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>Users: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=440, margin=dict(l=10, r=60, t=5, b=10),
        xaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
        yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=11)),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown("**Top 12 Databases**")
    df = cached("top_databases")
    DB_COLORS = {
        "PostgreSQL": "#4169e1", "MySQL": "#4479a1", "SQLite": "#003b57",
        "Microsoft SQL Server": "#cc2927", "MongoDB": "#47a248", "Redis": "#dc382d",
        "MariaDB": "#003545", "Elasticsearch": "#005571", "DynamoDB": "#ff9900",
        "Oracle": "#f80000", "Supabase": "#3ecf8e", "Cassandra": "#1287b1",
    }
    df["color"] = df["database_name"].map(DB_COLORS).fillna("#64748b")
    fig = go.Figure(go.Bar(
        x=df["users"], y=df["database_name"], orientation="h",
        marker_color=df["color"].tolist(),
        text=df["users"].apply(lambda v: f"{v/1000:.1f}k"),
        textposition="outside", textfont=dict(size=10, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>Users: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=440, margin=dict(l=10, r=60, t=5, b=10),
        xaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
        yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=11)),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

# Cloud platforms
st.markdown("**Top Cloud Platforms**")
df = cached("top_cloud_platforms")
CLOUD_COLORS = {
    "AWS": "#ff9900", "Azure": "#0078d4", "Google Cloud": "#4285f4",
    "Cloudflare": "#f48120", "Heroku": "#430098", "Vercel": "#e2e8f0",
    "DigitalOcean": "#0080ff", "Firebase": "#ffca28", "Netlify": "#00c7b7", "Hetzner": "#d50c2d",
}
df["color"] = df["cloud_platform"].map(CLOUD_COLORS).fillna("#64748b")
fig = go.Figure(go.Bar(
    x=df["users"], y=df["cloud_platform"], orientation="h",
    marker_color=df["color"].tolist(),
    text=df["users"].apply(lambda v: f"{v/1000:.1f}k"),
    textposition="outside", textfont=dict(size=11, color="#94a3b8"),
    hovertemplate="<b>%{y}</b><br>Users: %{x:,}<extra></extra>",
))
fig.update_layout(
    plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
    height=360, margin=dict(l=10, r=60, t=5, b=10),
    xaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
    yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=12)),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('<div class="insight-box">💡 AWS leads cloud by 2× over Azure. PostgreSQL overtook MySQL as the most-used database for the 3rd year running. Python is now #3 overall — closing in on JavaScript.</div>', unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 4: Remote Work ────────────────────────────────────────────────────
st.markdown('<div class="section-title">🌐 Remote Work Trends</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">How developers actually work in 2024 — remote, hybrid, or in-person</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    df = cached("remote_distribution")
    fig = go.Figure(go.Pie(
        labels=df["RemoteWork"],
        values=df["respondents"],
        hole=0.55,
        marker_colors=["#6d28d9", "#8b5cf6", "#334155"],
        textinfo="label+percent",
        textfont=dict(size=12, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>%{value:,} devs (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
        annotations=[dict(text="Work<br>Mode", x=0.5, y=0.5, font_size=14,
                          font_color="#94a3b8", showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df = cached("remote_by_experience")
    order = ["0–1 yrs", "2–4 yrs", "5–9 yrs", "10–19 yrs", "20+ yrs"]
    df["exp_bucket"] = pd.Categorical(df["exp_bucket"], categories=order, ordered=True)
    df = df.sort_values("exp_bucket")
    fig = go.Figure(go.Bar(
        x=df["exp_bucket"], y=df["remote_pct"],
        marker_color="#8b5cf6",
        text=df["remote_pct"].apply(lambda v: f"{v}%"),
        textposition="outside", textfont=dict(size=12, color="#94a3b8"),
        hovertemplate="<b>%{x}</b><br>Remote: %{y}%<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=10, t=20, b=10),
        title=dict(text="% Fully Remote by Experience Level", font=dict(color="#94a3b8", size=13)),
        xaxis=dict(showgrid=False, color="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b", title="Remote %"),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="insight-box">💡 Hybrid is the new normal — 42.5% work partly remote. Senior developers (10+ years) are more likely to work fully remote than juniors. Only 19.6% are fully in-person.</div>', unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 5: Developer Profile ─────────────────────────────────────────────
st.markdown('<div class="section-title">👤 Developer Profile</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Who responded — experience, education, employment, location</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    df = cached("experience_distribution")
    order = ["0–1 yrs", "2–4 yrs", "5–9 yrs", "10–19 yrs", "20+ yrs"]
    df["exp_bucket"] = pd.Categorical(df["exp_bucket"], categories=order, ordered=True)
    df = df.sort_values("exp_bucket")
    fig = go.Figure(go.Bar(
        x=df["exp_bucket"], y=df["respondents"],
        marker_color=["#1e3a5f", "#1d6fa4", "#2196d3", "#6d28d9", "#8b5cf6"],
        text=df["respondents"].apply(lambda v: f"{v/1000:.1f}k"),
        textposition="outside", textfont=dict(size=11, color="#94a3b8"),
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=10, t=20, b=10),
        title=dict(text="Experience Distribution", font=dict(color="#94a3b8", size=13)),
        xaxis=dict(showgrid=False, color="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df = cached("education_vs_salary")
    df = df.sort_values("median_salary", ascending=True).tail(8)
    fig = go.Figure(go.Bar(
        x=df["median_salary"], y=df["EdLevel"], orientation="h",
        marker_color="#6d28d9",
        text=df["median_salary"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="outside", textfont=dict(size=10, color="#94a3b8"),
    ))
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=70, t=20, b=10),
        title=dict(text="Median Salary by Education Level", font=dict(color="#94a3b8", size=13)),
        xaxis=dict(showgrid=True, gridcolor="#1e293b", tickformat="$,.0f", color="#64748b"),
        yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=10)),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

# Top countries by volume
df = cached("top_countries_by_volume")
fig = go.Figure(go.Bar(
    x=df["Country"], y=df["respondents"],
    marker_color="#4c1d95",
    text=df["respondents"].apply(lambda v: f"{v/1000:.1f}k"),
    textposition="outside", textfont=dict(size=11, color="#94a3b8"),
    hovertemplate="<b>%{x}</b><br>Respondents: %{y:,}<extra></extra>",
))
fig.update_layout(
    plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
    height=340, margin=dict(l=10, r=10, t=20, b=10),
    title=dict(text="Top 15 Countries by Survey Volume", font=dict(color="#94a3b8", size=13)),
    xaxis=dict(showgrid=False, color="#e2e8f0", tickangle=-30),
    yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b"),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 6: DA / DE Focus ──────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Data Roles Focus</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">What the data says about Data Analyst · Data Engineer · Data Scientist roles specifically</div>', unsafe_allow_html=True)

# SQL usage stat
sql_df = q.sql_usage_rate(conn)
py_r_df = q.python_vs_r_data(conn)
col1, col2, col3 = st.columns(3)
with col1:
    sql_pct = float(sql_df["sql_pct"].iloc[0])
    total_dp = int(sql_df["total_data_pros"].iloc[0])
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🗄️</div>
    <div class="kpi-label">SQL Adoption</div>
    <div class="kpi-value">{sql_pct}%</div>
    <div class="kpi-sub">of {total_dp:,} data pros use SQL</div></div>""", unsafe_allow_html=True)
with col2:
    py_row = py_r_df[py_r_df["language"] == "Python"]
    py_pct = float(py_row["adoption_pct"].iloc[0]) if not py_row.empty else 0
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🐍</div>
    <div class="kpi-label">Python Adoption</div>
    <div class="kpi-value">{py_pct}%</div>
    <div class="kpi-sub">of data professionals</div></div>""", unsafe_allow_html=True)
with col3:
    r_row = py_r_df[py_r_df["language"] == "R"]
    r_pct = float(r_row["adoption_pct"].iloc[0]) if not r_row.empty else 0
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📊</div>
    <div class="kpi-label">R Adoption</div>
    <div class="kpi-value">{r_pct}%</div>
    <div class="kpi-sub">of data professionals</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Data roles salary
df = cached("data_roles_salary")
fig = go.Figure(go.Bar(
    x=df["median_salary"], y=df["dev_type"], orientation="h",
    marker_color="#8b5cf6",
    text=df["median_salary"].apply(lambda v: f"${v/1000:.0f}k"),
    textposition="outside", textfont=dict(size=11, color="#94a3b8"),
    hovertemplate="<b>%{y}</b><br>Median: $%{x:,.0f}<br>Respondents: %{customdata:,}<extra></extra>",
    customdata=df["respondents"],
))
fig.update_layout(
    plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
    height=420, margin=dict(l=10, r=80, t=10, b=10),
    xaxis=dict(showgrid=True, gridcolor="#1e293b", tickformat="$,.0f", color="#64748b"),
    yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=12)),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig, use_container_width=True)

# AI adoption
df = cached("ai_tool_adoption")
fig = go.Figure(go.Bar(
    x=df["AISelect"], y=df["pct"],
    marker_color=["#8b5cf6", "#6d28d9", "#334155", "#1e293b"],
    text=df["pct"].apply(lambda v: f"{v}%"),
    textposition="outside", textfont=dict(size=13, color="#94a3b8"),
    hovertemplate="<b>%{x}</b><br>%{y}% of respondents<extra></extra>",
))
fig.update_layout(
    plot_bgcolor="#0f172a", paper_bgcolor="rgba(0,0,0,0)",
    height=320, margin=dict(l=10, r=10, t=20, b=10),
    title=dict(text="AI Tool Usage in Developer Workflow (2024)", font=dict(color="#94a3b8", size=13)),
    xaxis=dict(showgrid=False, color="#e2e8f0"),
    yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#64748b", title="%"),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="insight-box">💡 SQL is used by 69% of data professionals — the most universal skill in data. Python dominates with 75%+ adoption. R is used by only ~18% of data pros — Python won the data language war. Engineering Manager is the highest-paid "data-adjacent" role at $118k median.</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#475569;font-size:0.8rem;">'
    '📊 65,437 responses · 185 countries · 20 analytical queries · '
    'Data: <a href="https://survey.stackoverflow.co/2024" style="color:#a78bfa;">Stack Overflow Annual Survey 2024</a> · '
    'Built by <a href="https://github.com/evgeniimatveev" style="color:#a78bfa;">Evgenii Matveev</a>'
    '</div>',
    unsafe_allow_html=True,
)
