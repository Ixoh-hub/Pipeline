#!/usr/bin/env python3
"""Streamlit dashboard for patent data exploration."""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_database_connection():
    DB_PATH = Path("data/patent_pipeline.db")
    return sqlite3.connect(DB_PATH)

@st.cache_data
def load_data(query, _conn):
    return pd.read_sql_query(query, _conn)

def main():
    st.title("📊 Patent Intelligence Dashboard")
    st.markdown("Explore USPTO patent data with interactive visualizations and insights.")

    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Choose a view:",
                           ["Overview", "Inventors", "Companies", "Countries", "Trends"])

    conn = get_database_connection()

    if page == "Overview":
        show_overview(conn)
    elif page == "Inventors":
        show_inventors(conn)
    elif page == "Companies":
        show_companies(conn)
    elif page == "Countries":
        show_countries(conn)
    elif page == "Trends":
        show_trends(conn)

    conn.close()

def show_overview(conn):
    st.header("📈 Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_patents = load_data("SELECT COUNT(*) FROM patents", conn).iloc[0, 0]
        st.metric("Total Patents", f"{total_patents:,}")

    with col2:
        total_inventors = load_data("SELECT COUNT(*) FROM inventors", conn).iloc[0, 0]
        st.metric("Total Inventors", f"{total_inventors:,}")

    with col3:
        total_companies = load_data("SELECT COUNT(*) FROM companies", conn).iloc[0, 0]
        st.metric("Total Companies", f"{total_companies:,}")

    with col4:
        total_relationships = load_data("SELECT COUNT(*) FROM relationships", conn).iloc[0, 0]
        st.metric("Relationships", f"{total_relationships:,}")

    # Top insights
    st.subheader("🏆 Top Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Most Prolific Inventor")
        top_inventor = load_data("""
            SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            GROUP BY i.inventor_id, i.name
            ORDER BY patents DESC
            LIMIT 1
        """, conn)
        if not top_inventor.empty:
            st.write(f"**{top_inventor.iloc[0]['name']}**")
            st.write(f"Patents: {top_inventor.iloc[0]['patents']:,}")

    with col2:
        st.subheader("Largest Patent Holder")
        top_company = load_data("""
            SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            GROUP BY c.company_id, c.name
            ORDER BY patents DESC
            LIMIT 1
        """, conn)
        if not top_company.empty:
            st.write(f"**{top_company.iloc[0]['name']}**")
            st.write(f"Patents: {top_company.iloc[0]['patents']:,}")

def show_inventors(conn):
    st.header("👥 Inventor Analysis")

    # Top inventors
    st.subheader("Top Inventors by Patent Count")

    top_n = st.slider("Number of inventors to show:", 5, 50, 20)

    inventors_df = load_data(f"""
        SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name
        ORDER BY patents DESC
        LIMIT {top_n}
    """, conn)

    fig = px.bar(inventors_df, x='patents', y='name',
                 title=f'Top {top_n} Inventors by Patent Count',
                 labels={'patents': 'Number of Patents', 'name': 'Inventor'},
                 orientation='h')
    st.plotly_chart(fig, use_container_width=True)

    # Inventor search
    st.subheader("Search for Specific Inventor")
    inventor_name = st.text_input("Enter inventor name (partial match):")

    if inventor_name:
        search_results = load_data(f"""
            SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            WHERE i.name LIKE '%{inventor_name}%'
            GROUP BY i.inventor_id, i.name
            ORDER BY patents DESC
            LIMIT 10
        """, conn)

        if not search_results.empty:
            st.dataframe(search_results)
        else:
            st.write("No inventors found matching that name.")

def show_companies(conn):
    st.header("🏢 Company Analysis")

    # Top companies
    st.subheader("Top Companies by Patent Count")

    top_n = st.slider("Number of companies to show:", 5, 50, 20)

    companies_df = load_data(f"""
        SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patents DESC
        LIMIT {top_n}
    """, conn)

    fig = px.bar(companies_df, x='name', y='patents',
                 title=f'Top {top_n} Companies by Patent Count',
                 labels={'name': 'Company', 'patents': 'Number of Patents'})
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    # Company search
    st.subheader("Search for Specific Company")
    company_name = st.text_input("Enter company name (partial match):")

    if company_name:
        search_results = load_data(f"""
            SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            WHERE c.name LIKE '%{company_name}%'
            GROUP BY c.company_id, c.name
            ORDER BY patents DESC
            LIMIT 10
        """, conn)

        if not search_results.empty:
            st.dataframe(search_results)
        else:
            st.write("No companies found matching that name.")

def show_countries(conn):
    st.header("🌍 Country Analysis")

    # Country distribution
    st.subheader("Patent Distribution by Inventor Country")

    countries_df = load_data("""
        SELECT i.country, COUNT(DISTINCT r.patent_id) as patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        WHERE i.country IS NOT NULL AND i.country != '' AND i.country != 'Unknown'
        GROUP BY i.country
        ORDER BY patents DESC
        LIMIT 20
    """, conn)

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(countries_df, values='patents', names='country',
                        title='Patent Distribution by Country')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(countries_df.head(10), x='country', y='patents',
                        title='Top 10 Countries by Patent Count',
                        labels={'country': 'Country', 'patents': 'Number of Patents'})
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Country details
    st.subheader("Country Details")
    selected_country = st.selectbox("Select a country:",
                                   countries_df['country'].tolist())

    if selected_country:
        country_stats = load_data(f"""
            SELECT
                COUNT(DISTINCT r.patent_id) as total_patents,
                COUNT(DISTINCT r.inventor_id) as total_inventors,
                AVG(p.year) as avg_year
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            JOIN patents p ON r.patent_id = p.patent_id
            WHERE i.country = '{selected_country}'
        """, conn)

        if not country_stats.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Patents", f"{int(country_stats.iloc[0]['total_patents']):,}")
            with col2:
                st.metric("Total Inventors", f"{int(country_stats.iloc[0]['total_inventors']):,}")
            with col3:
                st.metric("Avg Patent Year", f"{country_stats.iloc[0]['avg_year']:.1f}")

def show_trends(conn):
    st.header("📈 Patent Trends")

    # Patent filings over time
    st.subheader("Patent Filings Over Time")

    trends_df = load_data("""
        SELECT year, COUNT(*) as patents
        FROM patents
        WHERE year IS NOT NULL AND year > 1900
        GROUP BY year
        ORDER BY year
    """, conn)

    fig = px.line(trends_df, x='year', y='patents',
                 title='Patent Filings by Year (1976-2023)',
                 labels={'year': 'Year', 'patents': 'Number of Patents'})
    st.plotly_chart(fig, use_container_width=True)

    # Year range selector
    st.subheader("Focus on Specific Years")
    min_year, max_year = st.slider("Select year range:",
                                  int(trends_df['year'].min()),
                                  int(trends_df['year'].max()),
                                  (2000, 2023))

    filtered_trends = trends_df[(trends_df['year'] >= min_year) &
                               (trends_df['year'] <= max_year)]

    fig_filtered = px.line(filtered_trends, x='year', y='patents',
                          title=f'Patent Filings ({min_year}-{max_year})',
                          labels={'year': 'Year', 'patents': 'Number of Patents'})
    st.plotly_chart(fig_filtered, use_container_width=True)

if __name__ == "__main__":
    main()