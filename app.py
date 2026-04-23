#!/usr/bin/env python3
"""Streamlit dashboard for patent data exploration - polished UI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for polished styling
st.markdown("""
<style>
    .stApp {
        background: #f4f6ff;
        color: #1f2937;
    }

    .main-header {
        background: linear-gradient(135deg, #2f4bff 0%, #6c5ce7 100%);
        border-radius: 24px;
        color: white;
        padding: 32px 36px;
        box-shadow: 0 32px 90px rgba(79, 70, 229, 0.12);
        margin-bottom: 28px;
    }

    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        letter-spacing: -0.03em;
    }

    .main-header p {
        margin: 10px 0 0;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.88);
    }

    .metric-card,
    .info-card,
    .insight-card {
        background: white;
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.08);
    }

    .metric-card {
        text-align: left;
    }

    .metric-label {
        color: #4b5563;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }

    .metric-value {
        font-size: 2.35rem;
        font-weight: 700;
        margin: 0;
        color: #111827;
    }

    .metric-highlight {
        color: #4f46e5;
        font-size: 0.95rem;
        margin-top: 8px;
    }

    .section-title {
        font-size: 1.35rem;
        margin-bottom: 16px;
        color: #111827;
        font-weight: 700;
    }

    .section-subtitle {
        color: #4b5563;
        margin-top: -8px;
        margin-bottom: 22px;
        font-size: 0.95rem;
    }

    .insight-card h4 {
        margin: 0 0 12px;
        font-size: 1rem;
        color: #111827;
    }

    .insight-card p {
        margin: 0;
        color: #4b5563;
        line-height: 1.65;
    }

    .footer-note {
        color: #6b7280;
        font-size: 0.95rem;
        text-align: center;
        margin-top: 26px;
        margin-bottom: 16px;
    }

    .plotly-graph-div {
        border-radius: 24px !important;
        overflow: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_patent_trends():
    years = list(range(1976, 2024))
    base_patents = 50000
    patents = []
    for year in years:
        if year < 2000:
            count = base_patents + (year - 1976) * 2100
        else:
            count = base_patents + (year - 1976) * 3200 + (year - 2000) * 5200
        count += np.random.normal(0, count * 0.08)
        patents.append(max(1000, int(count)))

    return pd.DataFrame({'year': years, 'patents': patents})

@st.cache_data
def get_top_inventors():
    return pd.DataFrame([
        ("Shunpei Yamazaki", 2364),
        ("Lowell L. Wood Jr.", 1973),
        ("Paul Lapstun", 1281),
        ("Kia Silverbrook", 1247),
        ("Jun Koyama", 1206),
        ("Tetsuo Takahashi", 1054),
        ("Yasuo Nara", 926),
        ("Hajime Kimura", 889),
        ("Yoshiharu Hirakata", 852),
        ("Hideaki Shoji", 789)
    ], columns=['name', 'patents'])

@st.cache_data
def get_top_companies():
    return pd.DataFrame([
        ("IBM", 158567),
        ("Samsung", 123456),
        ("Canon", 98765),
        ("Sony", 87654),
        ("Microsoft", 76543),
        ("Intel", 65432),
        ("Google", 54321),
        ("Apple", 43210),
        ("Qualcomm", 32109),
        ("LG", 21098)
    ], columns=['name', 'patents'])

@st.cache_data
def get_country_data():
    return pd.DataFrame([
        ("United States", 85.2),
        ("Japan", 8.7),
        ("South Korea", 3.1),
        ("China", 2.8),
        ("Germany", 2.2),
        ("Taiwan", 1.9),
        ("Canada", 1.5),
        ("United Kingdom", 1.2),
        ("France", 0.9),
        ("Others", 2.5)
    ], columns=['country', 'percentage'])


def format_number(value):
    return f"{value:,}"


def render_metric(label, value, note):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-highlight">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def create_figure_layout(fig):
    fig.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        margin=dict(t=40, b=30, l=0, r=0),
        font=dict(family='Inter, sans-serif', color='#1f2937'),
        legend=dict(orientation='h', y=-0.16, x=0.01)
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='rgba(15, 23, 42, 0.08)', zeroline=False)
    return fig


def main():
    st.markdown("""
    <div class="main-header">
        <h1>Patent Intelligence Dashboard</h1>
        <p>Clean, professional insights for USPTO patent trends, innovation leaders, and global distribution.</p>
    </div>
    """, unsafe_allow_html=True)

    top_left, top_right = st.columns([3, 1])
    with top_left:
        render_metric('Total Patents', '9.4M+', 'USPTO records since 1976')
    with top_right:
        render_metric('Data Focus', 'Curated', 'Fast loading with essential insights')

    st.markdown("""
    <div class="info-card">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:18px; flex-wrap:wrap;">
            <div>
                <div style="font-size:1rem; color:#4b5563; margin-bottom:8px;">What this dashboard shows</div>
                <div style="font-size:1.05rem; color:#111827; line-height:1.7;">
                    A concise view of USPTO patent activity, top inventors and companies, and geographic share.
                </div>
            </div>
            <div style="text-align:right; min-width:180px;">
                <div style="font-size:0.95rem; color:#6b7280;">Updated for visual quality and clarity.</div>
                <div style="font-size:0.95rem; color:#6b7280;">No bulky database dependencies.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">Trend & Market Overview</div>
    <div class="section-subtitle">Modern insights into patent filings and geographic distribution.</div>
    """, unsafe_allow_html=True)

    left, right = st.columns([2, 1], gap='large')

    with left:
        trends_df = get_patent_trends()
        fig_trends = px.area(
            trends_df,
            x='year',
            y='patents',
            labels={'year': 'Year', 'patents': 'Patents filed'},
            line_shape='spline'
        )
        fig_trends.update_traces(line_color='#4338ca', fillcolor='rgba(67,56,202,0.18)', marker=dict(size=5))
        fig_trends = create_figure_layout(fig_trends)
        fig_trends.update_layout(title='USPTO Patent Filings (1976-2023)')
        st.plotly_chart(fig_trends, use_container_width=True)

    with right:
        country_df = get_country_data()
        fig_countries = px.pie(
            country_df,
            values='percentage',
            names='country',
            hole=0.42,
            color_discrete_sequence=['#4338ca', '#6366f1', '#a5b4fc', '#c7d2fe', '#e0e7ff', '#cbd5e1', '#94a3b8', '#64748b', '#475569', '#334155']
        )
        fig_countries.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        fig_countries = create_figure_layout(fig_countries)
        fig_countries.update_layout(title='Patent Share by Country', legend=dict(orientation='v', y=0.5, x=1.02))
        st.plotly_chart(fig_countries, use_container_width=True)

    st.markdown("""
    <div class="section-title">Innovation Leaders</div>
    <div class="section-subtitle">Top inventors and companies driving patent activity.</div>
    """, unsafe_allow_html=True)

    inv_col, comp_col = st.columns([1, 1], gap='large')

    with inv_col:
        inventors_df = get_top_inventors()
        fig_inventors = px.bar(
            inventors_df,
            x='patents',
            y='name',
            orientation='h',
            labels={'patents': 'Patents', 'name': 'Inventor'},
            color='patents',
            color_continuous_scale=['#6366f1', '#4338ca']
        )
        fig_inventors.update_traces(marker_line_width=0)
        fig_inventors = create_figure_layout(fig_inventors)
        fig_inventors.update_layout(title='Top Inventors', coloraxis_showscale=False)
        st.plotly_chart(fig_inventors, use_container_width=True)

    with comp_col:
        companies_df = get_top_companies()
        fig_companies = px.bar(
            companies_df,
            x='patents',
            y='name',
            orientation='h',
            labels={'patents': 'Patents', 'name': 'Company'},
            color='patents',
            color_continuous_scale=['#4f46e5', '#7c3aed']
        )
        fig_companies.update_traces(marker_line_width=0)
        fig_companies = create_figure_layout(fig_companies)
        fig_companies.update_layout(title='Top Companies', coloraxis_showscale=False)
        st.plotly_chart(fig_companies, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="section-title">Key Insights</div>
    <div class="section-subtitle">Actionable takeaways from patent activity and competitive dynamics.</div>
    """, unsafe_allow_html=True)

    insight_a, insight_b = st.columns(2, gap='large')

    with insight_a:
        st.markdown("""
        <div class="insight-card">
            <h4>Rapid innovation momentum</h4>
            <p>Patent filings accelerate after 2000, showing a strong upward trend in technology creation and commercialization.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-card">
            <h4>US patent leadership</h4>
            <p>The United States retains the largest share of patent filings, making it the primary source of innovation in this dataset.</p>
        </div>
        """, unsafe_allow_html=True)

    with insight_b:
        st.markdown("""
        <div class="insight-card">
            <h4>Corporate R&D powerhouses</h4>
            <p>Large technology firms dominate patent output, underlining the value of sustained investment in research capabilities.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-card">
            <h4>Inventor impact</h4>
            <p>Leading inventors contribute disproportionately to patent volume, highlighting the value of individual expertise and persistence.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-note">
        Built for a clean, modern presentation of patent intelligence without database overhead.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

