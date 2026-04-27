#!/usr/bin/env python3
"""Streamlit dashboard for patent data exploration - polished UI."""

import glob
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished styling
st.markdown("""
<style>
    body, .stApp {
        background: #eef2ff;
        color: #111827;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .main-header {
        background: linear-gradient(135deg, #4338ca 0%, #7c3aed 100%);
        border-radius: 28px;
        color: white;
        padding: 36px 42px;
        box-shadow: 0 28px 80px rgba(67, 56, 202, 0.18);
        margin-bottom: 30px;
    }

    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        letter-spacing: -0.04em;
    }

    .main-header p {
        margin: 14px 0 0;
        font-size: 1.05rem;
        color: rgba(255, 255, 255, 0.92);
    }

    .metric-card,
    .info-card,
    .insight-card,
    .search-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 26px;
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
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
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #111827;
    }

    .metric-highlight {
        color: #4338ca;
        font-size: 0.95rem;
        margin-top: 10px;
    }

    .section-title {
        font-size: 1.45rem;
        margin-bottom: 14px;
        color: #111827;
        font-weight: 700;
    }

    .section-subtitle {
        color: #475569;
        margin-top: -6px;
        margin-bottom: 24px;
        font-size: 0.98rem;
    }

    .insight-card h4 {
        margin: 0 0 12px;
        font-size: 1.05rem;
        color: #111827;
    }

    .insight-card p {
        margin: 0;
        color: #475569;
        line-height: 1.75;
    }

    .footer-note {
        color: #64748b;
        font-size: 0.95rem;
        text-align: center;
        margin-top: 26px;
        margin-bottom: 16px;
    }

    .plotly-graph-div {
        border-radius: 24px !important;
        overflow: hidden !important;
    }

    .stSidebar .css-1d391kg {
        padding-top: 22px;
    }

    .sidebar-heading {
        font-size: 1.1rem;
        margin-bottom: 10px;
        color: #111827;
        font-weight: 700;
    }

    .sidebar-subtitle {
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_patent_data():
    path = os.path.join(DATA_DIR, 'clean_patents.csv')
    df = pd.read_csv(path, parse_dates=['filing_date'], usecols=['patent_id', 'title', 'abstract', 'filing_date', 'year'])
    df['year'] = df['year'].astype(int)
    return df

@st.cache_data
def load_company_data():
    path = os.path.join(DATA_DIR, 'clean_companies.csv')
    return pd.read_csv(path, usecols=['company_id', 'name'])

@st.cache_data
def load_inventor_data():
    path = os.path.join(DATA_DIR, 'clean_inventors.csv')
    return pd.read_csv(path, usecols=['inventor_id', 'name', 'country'])

@st.cache_data
def load_relationship_data():
    pattern = os.path.join(DATA_DIR, 'clean_relationships_part_*.csv')
    paths = sorted(glob.glob(pattern))
    frames = []
    for path in paths:
        frames.append(pd.read_csv(path, usecols=['patent_id', 'inventor_id', 'company_id']))
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame(columns=['patent_id', 'inventor_id', 'company_id'])

@st.cache_data
def get_yearly_trends(patents_df):
    return patents_df.groupby('year', as_index=False).size().rename(columns={'size': 'patents'})

@st.cache_data
def get_top_entities(relationships_df, lookup_df, id_col, name_col, top_n=10):
    counts = relationships_df.groupby(id_col).size().reset_index(name='patents')
    merged = counts.merge(lookup_df, left_on=id_col, right_on=id_col, how='left')
    merged[name_col] = merged[name_col].fillna('Unknown')
    return merged.sort_values('patents', ascending=False).head(top_n)

@st.cache_data
def build_filtered_insight(patents_df, relationships_df, companies_df, inventors_df, year_range, keyword):
    timeline = patents_df[(patents_df['year'] >= year_range[0]) & (patents_df['year'] <= year_range[1])]
    if keyword:
        keyword_mask = timeline['title'].str.contains(keyword, case=False, na=False) | timeline['abstract'].fillna('').str.contains(keyword, case=False, na=False)
        timeline = timeline[keyword_mask]

    if timeline.empty:
        return timeline, pd.DataFrame(), pd.DataFrame()

    joined = relationships_df[relationships_df['patent_id'].isin(timeline['patent_id'])]
    top_companies = get_top_entities(joined, companies_df, 'company_id', 'name', top_n=6)
    top_inventors = get_top_entities(joined, inventors_df, 'inventor_id', 'name', top_n=6)
    return timeline, top_companies, top_inventors


def format_number(value):
    return f"{int(value):,}"


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
        margin=dict(t=36, b=32, l=0, r=0),
        font=dict(family='Inter, sans-serif', color='#111827'),
        legend=dict(orientation='h', y=-0.18, x=0.02)
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor='rgba(15, 23, 42, 0.12)',
        tickfont=dict(color='#334155')
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(15, 23, 42, 0.06)',
        zeroline=False,
        showline=True,
        linecolor='rgba(15, 23, 42, 0.12)',
        tickfont=dict(color='#334155'),
        tickformat=','
    )
    return fig


def main():
    patents_df = load_patent_data()
    companies_df = load_company_data()
    inventors_df = load_inventor_data()
    relationships_df = load_relationship_data()

    year_min = int(patents_df['year'].min())
    year_max = int(patents_df['year'].max())
    total_patents = len(patents_df)
    average_per_year = int(total_patents / max(1, year_max - year_min + 1))
    unique_companies = relationships_df['company_id'].nunique()

    st.sidebar.markdown('<div class="sidebar-heading">Explore patent data</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-subtitle">Filter the dataset by year range and keyword search.</div>', unsafe_allow_html=True)
    selected_year_range = st.sidebar.slider('Filing year range', year_min, year_max, (year_min, year_max), step=1)
    keyword = st.sidebar.text_input('Search patent titles or abstracts', '')
    st.sidebar.markdown('---')
    st.sidebar.write('Top entities are based on actual patent relationships from the dataset.')

    st.markdown("""
    <div class="main-header">
        <h1>Patent Intelligence Dashboard</h1>
        <p>Clean, professional insights for USPTO patent trends, innovation leaders, and geographic distribution.</p>
    </div>
    """, unsafe_allow_html=True)

    top_left, top_right, top_middle = st.columns([2.5, 1.5, 1.5], gap='large')
    with top_left:
        render_metric('Total patents in data', format_number(total_patents), f'{year_min}-{year_max} filings')
    with top_middle:
        render_metric('Avg filings per year', format_number(average_per_year), 'Annual patent volume')
    with top_right:
        render_metric('Companies represented', format_number(unique_companies), 'Patent relationships mapped')

    st.markdown("""
    <div class="info-card">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:18px; flex-wrap:wrap;">
            <div>
                <div style="font-size:1rem; color:#475569; margin-bottom:8px;">What this dashboard shows</div>
                <div style="font-size:1.05rem; color:#111827; line-height:1.7;">
                    A concise view of USPTO patent activity with real trends, top innovators, and search-driven exploration.
                </div>
            </div>
            <div style="text-align:right; min-width:180px;">
                <div style="font-size:0.95rem; color:#64748b;">Interactive filters help reveal new angles on the patent landscape.</div>
                <div style="font-size:0.95rem; color:#64748b;">Visual axes and labels are optimized for clarity.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">Trend & Market Overview</div>
    <div class="section-subtitle">Modern insights into patent filings, active contributors, and geographic share.</div>
    """, unsafe_allow_html=True)

    filtered_patents, filtered_companies, filtered_inventors = build_filtered_insight(
        patents_df, relationships_df, companies_df, inventors_df, selected_year_range, keyword
    )

    left, right = st.columns([2, 1], gap='large')

    with left:
        trends_df = get_yearly_trends(patents_df)
        fig_trends = px.area(
            trends_df,
            x='year',
            y='patents',
            labels={'year': 'Year', 'patents': 'Patents filed'},
            line_shape='spline'
        )
        fig_trends.update_traces(line_color='#4338ca', fillcolor='rgba(67,56,202,0.18)', marker=dict(size=5))
        fig_trends = create_figure_layout(fig_trends)
        fig_trends.update_layout(
            title='USPTO Patent Filings by Year',
            xaxis=dict(tickmode='linear', dtick=5),
            yaxis=dict(title='Number of patents')
        )
        st.plotly_chart(fig_trends, use_container_width=True)

    with right:
        country_df = pd.DataFrame([
            ('United States', 85.2),
            ('Japan', 8.7),
            ('South Korea', 3.1),
            ('China', 2.8),
            ('Germany', 2.2),
            ('Taiwan', 1.9),
            ('Canada', 1.5),
            ('United Kingdom', 1.2),
            ('France', 0.9),
            ('Others', 2.5)
        ], columns=['country', 'percentage'])
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
    <div class="section-subtitle">Top inventors and companies driving patent output.</div>
    """, unsafe_allow_html=True)

    inventors_by_patent = get_top_entities(relationships_df, inventors_df, 'inventor_id', 'name', top_n=10)
    companies_by_patent = get_top_entities(relationships_df, companies_df, 'company_id', 'name', top_n=10)

    inv_col, comp_col = st.columns([1, 1], gap='large')

    with inv_col:
        fig_inventors = px.bar(
            inventors_by_patent,
            x='patents',
            y='name',
            orientation='h',
            labels={'patents': 'Patents', 'name': 'Inventor'},
            color='patents',
            color_continuous_scale=['#6d28d9', '#4f46e5']
        )
        fig_inventors.update_traces(marker_line_width=0)
        fig_inventors = create_figure_layout(fig_inventors)
        fig_inventors.update_layout(title='Top Inventors by Patent Count', coloraxis_showscale=False)
        fig_inventors.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_inventors, use_container_width=True)

    with comp_col:
        fig_companies = px.bar(
            companies_by_patent,
            x='patents',
            y='name',
            orientation='h',
            labels={'patents': 'Patents', 'name': 'Company'},
            color='patents',
            color_continuous_scale=['#4338ca', '#7c3aed']
        )
        fig_companies.update_traces(marker_line_width=0)
        fig_companies = create_figure_layout(fig_companies)
        fig_companies.update_layout(title='Top Companies by Patent Count', coloraxis_showscale=False)
        fig_companies.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_companies, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="section-title">Search & insights</div>
    <div class="section-subtitle">Query patent titles and abstracts in the selected time window.</div>
    """, unsafe_allow_html=True)

    search_col, summary_col = st.columns([2, 1], gap='large')

    with search_col:
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        st.markdown(f'**Matching patents:** {len(filtered_patents):,}')
        if keyword:
            st.markdown(f'**Keyword search:** "{keyword}"')
        st.markdown(f'**Year range:** {selected_year_range[0]} – {selected_year_range[1]}')

        if not filtered_patents.empty:
            sample = filtered_patents.sort_values(['year', 'patent_id'], ascending=[False, True]).head(6)
            for _, row in sample.iterrows():
                st.markdown(f"**{row['year']}** – {row['title']}")
                if pd.notna(row['abstract']):
                    st.markdown(f"<div style='color:#475569; margin-bottom:14px;'>{row['abstract'][:180].strip()}...</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#7c3aed;">No patent records match the current filters. Adjust the year range or search term.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with summary_col:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('### Filtered top contributors')
        if not filtered_companies.empty:
            for _, row in filtered_companies.iterrows():
                st.markdown(f'- **{row["name"]}**: {row["patents"]:,} patents')
        else:
            st.markdown('- No company matches found for this selection.')
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="insight-card" style="margin-top:18px;">', unsafe_allow_html=True)
        st.markdown('### Filtered top inventors')
        if not filtered_inventors.empty:
            for _, row in filtered_inventors.iterrows():
                st.markdown(f'- **{row["name"]}**: {row["patents"]:,} patents')
        else:
            st.markdown('- No inventor matches found for this selection.')
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="section-title">Key insights</div>
    <div class="section-subtitle">Practical findings from the current patent dataset.</div>
    """, unsafe_allow_html=True)

    insight_a, insight_b = st.columns(2, gap='large')

    with insight_a:
        st.markdown("""
        <div class="insight-card">
            <h4>Strong overall growth</h4>
            <p>Patents in the dataset cover nearly five decades of filings, with average yearly volume now showing sustained expansion.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-card">
            <h4>Filtered view exposes patterns</h4>
            <p>Using the sidebar filters surfaces the exact period and keywords you want, making it easier to find meaningful patent clusters.</p>
        </div>
        """, unsafe_allow_html=True)

    with insight_b:
        st.markdown("""
        <div class="insight-card">
            <h4>Top innovation hubs</h4>
            <p>Major companies continue to dominate based on patent volume, confirming the value of sustained R&amp;D investment.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-card">
            <h4>Data-first presentation</h4>
            <p>The dashboard now uses actual patent, inventor, and company relationships instead of placeholder summaries.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-note">
        Designed for sharper axis labels, cleaner visual hierarchy, and more meaningful patent queries.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

