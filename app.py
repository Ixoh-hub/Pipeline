#!/usr/bin/env python3
"""Streamlit dashboard for patent data exploration."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import sys
from database_utils import execute_query

# Database initialization - now handled automatically by database_utils
@st.cache_resource
def initialize_database():
    # Check if we can connect to database
    try:
        test_query = "SELECT COUNT(*) FROM patents LIMIT 1"
        result = execute_query(test_query)
        if result.empty:
            raise Exception("No data found")
        return True
    except Exception as e:
        st.error(f"""
        ❌ **Database Connection Failed**
        
        {str(e)}
        
        **For Local Development:**
        - Run `python patent_pipeline.py` to generate the database
        
        **For Streamlit Cloud (Recommended):**
        - Upload `data/patent_pipeline.db` to Google Drive, AWS S3, or similar
        - Get a shareable download URL
        - Set `DATABASE_URL` in Streamlit Cloud secrets
        - The app will automatically download the database on startup
        
        **Alternative: Supabase PostgreSQL**
        - Set `SUPABASE_URL` and `SUPABASE_DB_PASSWORD` in secrets
        - Upload data to Supabase database (see SUPABASE_SETUP.md)
        
        See FINAL_DEPLOYMENT_GUIDE.md for complete instructions.
        """)
        st.stop()

# Initialize on first run
DB_PATH = initialize_database()

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "USPTO Patent Intelligence Dashboard - Explore 9M+ patents with interactive visualizations"
    }
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
    }
    .insight-box {
        background: #f0f2f6;
        padding: 15px;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    h1 { color: #667eea; font-weight: 700; }
    h2 { color: #764ba2; font-weight: 600; }
    h3 { color: #667eea; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# Database connection with proper configuration
@st.cache_resource
def get_database_connection():
    # This function is now handled by database_utils
    return None  # Not needed anymore

@st.cache_data
def load_data(query):
    try:
        return execute_query(query)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def main():
    # Header with gradient
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0;">📊 Patent Intelligence Dashboard</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">Explore 9.4M+ USPTO patents with interactive visualizations and insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.markdown("## 🗂️ Navigation")
    page = st.sidebar.radio(
        "Choose a view:",
        ["🏠 Overview", "👥 Inventors", "🏢 Companies", "🌍 Countries", "📈 Trends", "📊 Visualizations"],
        key="page_selection"
    )

    # Route to appropriate page
    if page == "🏠 Overview":
        show_overview()
    elif page == "👥 Inventors":
        show_inventors()
    elif page == "🏢 Companies":
        show_companies()
    elif page == "🌍 Countries":
        show_countries()
    elif page == "📈 Trends":
        show_trends()
    elif page == "📊 Visualizations":
        show_visualizations()

def show_overview():
    st.markdown("## 📈 Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    try:
        with col1:
            total_patents = load_data("SELECT COUNT(*) as count FROM patents").iloc[0, 0]
            st.metric("📜 Total Patents", f"{total_patents:,}", delta="9.4M+")

        with col2:
            total_inventors = load_data("SELECT COUNT(*) as count FROM inventors").iloc[0, 0]
            st.metric("👤 Inventors", f"{total_inventors:,}", delta="4.5M+")

        with col3:
            total_companies = load_data("SELECT COUNT(*) as count FROM companies").iloc[0, 0]
            st.metric("🏢 Companies", f"{total_companies:,}", delta="2.1M+")

        with col4:
            total_relationships = load_data("SELECT COUNT(*) as count FROM relationships").iloc[0, 0]
            st.metric("🔗 Relationships", f"{total_relationships:,}", delta="23M+")
    except Exception as e:
        st.error(f"Error loading key metrics: {e}")
        return

    # Top insights with custom styling
    st.markdown("### 🏆 Top Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Most Prolific Inventor")
        try:
            top_inventor = load_data("""
                SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
                FROM inventors i
                JOIN relationships r ON i.inventor_id = r.inventor_id
                GROUP BY i.inventor_id, i.name
                ORDER BY patents DESC
                LIMIT 1
            """)
            if not top_inventor.empty:
                name = top_inventor.iloc[0]['name']
                patents = top_inventor.iloc[0]['patents']
                st.markdown(f"""
                <div class="insight-box">
                    <strong>{name}</strong><br>
                    <span style="color: #667eea; font-size: 18px; font-weight: bold;">{patents:,} patents</span>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Could not load inventor data: {e}")

    with col2:
        st.markdown("#### Largest Patent Holder")
        try:
            top_company = load_data("""
                SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
                FROM companies c
                JOIN relationships r ON c.company_id = r.company_id
                GROUP BY c.company_id, c.name
                ORDER BY patents DESC
                LIMIT 1
            """)
            if not top_company.empty:
                name = top_company.iloc[0]['name']
                patents = top_company.iloc[0]['patents']
                st.markdown(f"""
                <div class="insight-box">
                    <strong>{name}</strong><br>
                    <span style="color: #764ba2; font-size: 18px; font-weight: bold;">{patents:,} patents</span>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Could not load company data: {e}")

def show_inventors():
    st.markdown("## 👥 Inventor Analysis")

    # Top inventors
    st.markdown("### Top Inventors by Patent Count")

    top_n = st.slider("Number of inventors to show:", 5, 50, 20, key="inventor_slider")

    try:
        inventors_df = load_data(f"""
            SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            GROUP BY i.inventor_id, i.name
            ORDER BY patents DESC
            LIMIT {top_n}
        """)

        if not inventors_df.empty:
            fig = px.bar(inventors_df, y='name', x='patents',
                         title=f'Top {top_n} Inventors by Patent Count',
                         labels={'patents': 'Number of Patents', 'name': 'Inventor'},
                         orientation='h',
                         color='patents',
                         color_continuous_scale='Viridis')
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading inventors: {e}")

    # Inventor search
    st.markdown("### 🔍 Search for Specific Inventor")
    inventor_name = st.text_input("Enter inventor name (partial match):", key="inventor_search")

    if inventor_name and len(inventor_name) >= 2:
        try:
            search_results = load_data(f"""
                SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
                FROM inventors i
                JOIN relationships r ON i.inventor_id = r.inventor_id
                WHERE LOWER(i.name) LIKE LOWER('%{inventor_name}%')
                GROUP BY i.inventor_id, i.name
                ORDER BY patents DESC
                LIMIT 10
            """)

            if not search_results.empty:
                st.dataframe(search_results, use_container_width=True)
            else:
                st.info("No inventors found matching that name.")
        except Exception as e:
            st.error(f"Search error: {e}")

def show_companies():
    st.markdown("## 🏢 Company Analysis")

    # Top companies
    st.markdown("### Top Companies by Patent Count")

    top_n = st.slider("Number of companies to show:", 5, 50, 20, key="company_slider")

    try:
        companies_df = load_data(f"""
            SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            GROUP BY c.company_id, c.name
            ORDER BY patents DESC
            LIMIT {top_n}
        """)

        if not companies_df.empty:
            fig = px.bar(companies_df, x='name', y='patents',
                         title=f'Top {top_n} Companies by Patent Count',
                         labels={'name': 'Company', 'patents': 'Number of Patents'},
                         color='patents',
                         color_continuous_scale='Blues')
            fig.update_xaxes(tickangle=45)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading companies: {e}")

    # Company search
    st.markdown("### 🔍 Search for Specific Company")
    company_name = st.text_input("Enter company name (partial match):", key="company_search")

    if company_name and len(company_name) >= 2:
        try:
            search_results = load_data(f"""
                SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
                FROM companies c
                JOIN relationships r ON c.company_id = r.company_id
                WHERE LOWER(c.name) LIKE LOWER('%{company_name}%')
                GROUP BY c.company_id, c.name
                ORDER BY patents DESC
                LIMIT 10
            """)

            if not search_results.empty:
                st.dataframe(search_results, use_container_width=True)
            else:
                st.info("No companies found matching that name.")
        except Exception as e:
            st.error(f"Search error: {e}")

def show_countries():
    st.markdown("## 🌍 Country Analysis")

    # Country distribution
    st.markdown("### Patent Distribution by Inventor Country")

    try:
        countries_df = load_data("""
            SELECT i.country, COUNT(DISTINCT r.patent_id) as patents
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            WHERE i.country IS NOT NULL AND i.country != '' AND i.country != 'Unknown'
            GROUP BY i.country
            ORDER BY patents DESC
            LIMIT 20
        """)

        if not countries_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig_pie = px.pie(countries_df, values='patents', names='country',
                                title='Patent Distribution by Country',
                                color_discrete_sequence=px.colors.sequential.Viridis)
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                fig_bar = px.bar(countries_df.head(10), x='country', y='patents',
                                title='Top 10 Countries by Patent Count',
                                labels={'country': 'Country', 'patents': 'Number of Patents'},
                                color='patents',
                                color_continuous_scale='Reds')
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)

            # Country details
            st.markdown("### Country Details")
            selected_country = st.selectbox("Select a country:",
                                           countries_df['country'].tolist(),
                                           key="country_select")

            if selected_country:
                country_stats = load_data(f"""
                    SELECT
                        COUNT(DISTINCT r.patent_id) as total_patents,
                        COUNT(DISTINCT r.inventor_id) as total_inventors,
                        AVG(CAST(p.year AS FLOAT)) as avg_year
                    FROM inventors i
                    JOIN relationships r ON i.inventor_id = r.inventor_id
                    JOIN patents p ON r.patent_id = p.patent_id
                    WHERE i.country = '{selected_country}'
                """)

                if not country_stats.empty:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📜 Total Patents", f"{int(country_stats.iloc[0]['total_patents']):,}")
                    with col2:
                        st.metric("👥 Total Inventors", f"{int(country_stats.iloc[0]['total_inventors']):,}")
                    with col3:
                        avg_year = country_stats.iloc[0]['avg_year']
                        if avg_year:
                            st.metric("📅 Avg Patent Year", f"{avg_year:.0f}")
    except Exception as e:
        st.error(f"Error loading countries data: {e}")

def show_trends():
    st.markdown("## 📈 Patent Trends Over Time")

    # Patent filings over time
    st.markdown("### Patent Filings by Year")

    try:
        trends_df = load_data("""
            SELECT year, COUNT(*) as patents
            FROM patents
            WHERE year IS NOT NULL AND year > 1970
            GROUP BY year
            ORDER BY year
        """)

        if not trends_df.empty:
            fig = px.line(trends_df, x='year', y='patents',
                         title='Patent Filings by Year (1970-2023)',
                         labels={'year': 'Year', 'patents': 'Number of Patents'},
                         markers=True)
            fig.update_traces(line=dict(color='#667eea', width=3), marker=dict(size=6))
            st.plotly_chart(fig, use_container_width=True)

            # Year range selector
            st.markdown("### Focus on Specific Year Range")
            min_year, max_year = st.slider("Select year range:",
                                          int(trends_df['year'].min()),
                                          int(trends_df['year'].max()),
                                          (2000, 2023),
                                          key="year_range")

            filtered_trends = trends_df[(trends_df['year'] >= min_year) &
                                       (trends_df['year'] <= max_year)]

            fig_filtered = px.bar(filtered_trends, x='year', y='patents',
                                 title=f'Patent Filings ({min_year}-{max_year})',
                                 labels={'year': 'Year', 'patents': 'Number of Patents'},
                                 color='patents',
                                 color_continuous_scale='Reds')
            st.plotly_chart(fig_filtered, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading trends: {e}")

def show_visualizations():
    st.markdown("## 📊 Generated Visualizations")
    
    st.markdown("""
    This section displays pre-generated visualizations and reports from the patent analysis.
    These comprehensive charts provide insights into patent trends, inventors, and companies.
    """)

    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        st.warning("Reports directory not found. Please run create_visualizations.py first.")
        return

    # Organize visualizations by category
    viz_tabs = st.tabs(["📈 Patent Trends", "👥 Inventors", "🏢 Companies", "🌍 Countries", "💡 Analysis"])

    with viz_tabs[0]:
        st.markdown("### Patent Trends and Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if (reports_dir / "patent_trends.png").exists():
                st.image(str(reports_dir / "patent_trends.png"), 
                        caption="Patent Trends Over Years",
                        use_column_width=True)
            
            if (reports_dir / "patent_counts_by_year.png").exists():
                st.image(str(reports_dir / "patent_counts_by_year.png"),
                        caption="Patent Counts by Year (2010-2023)",
                        use_column_width=True)
        
        with col2:
            if (reports_dir / "country_distribution.png").exists():
                st.image(str(reports_dir / "country_distribution.png"),
                        caption="Geographic Distribution of Patents",
                        use_column_width=True)
            
            if (reports_dir / "patent_counts_by_year.png").exists():
                st.markdown("**📊 Key Insights:**")
                st.markdown("""
                - Patent filings show growth trends from 1976 onwards
                - Significant increases observed from 2000-2020
                - Geographic diversity in patent distribution
                """)

    with viz_tabs[1]:
        st.markdown("### Inventor Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if (reports_dir / "top_inventors_chart.png").exists():
                st.image(str(reports_dir / "top_inventors_chart.png"),
                        caption="Top Inventors by Patent Count",
                        use_column_width=True)
        
        with col2:
            st.markdown("**🎯 Top Inventor Insights:**")
            st.markdown("""
            - Shunpei Yamazaki leads with 600+ patents
            - Strong presence from semiconductor and LCD technologies
            - Global inventor participation from multiple countries
            - Collaborative efforts drive innovation
            """)

    with viz_tabs[2]:
        st.markdown("### Company Patent Portfolio")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if (reports_dir / "company_analysis.png").exists():
                st.image(str(reports_dir / "company_analysis.png"),
                        caption="Top Companies by Patent Count",
                        use_column_width=True)
        
        with col2:
            st.markdown("**🏆 Company Insights:**")
            st.markdown("""
            - Samsung leads with 5000+ patents
            - IBM, Sony, and other tech giants follow
            - Technology sector dominates patent creation
            - Strategic focus on semiconductor and software patents
            """)

    with viz_tabs[3]:
        st.markdown("### Geographic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if (reports_dir / "top_countries_basic.png").exists():
                st.image(str(reports_dir / "top_countries_basic.png"),
                        caption="Top Countries by Inventor Count",
                        use_column_width=True)
        
        with col2:
            st.markdown("**🌐 Geographic Insights:**")
            st.markdown("""
            - USA and Japan lead in patent innovation
            - Strong presence from European countries
            - Growing participation from Asian nations
            - International collaboration on patents
            """)

    with viz_tabs[4]:
        st.markdown("### Advanced Analysis Reports")
        
        # Interactive visualizations
        if (reports_dir / "interactive_trends.html").exists():
            st.markdown("#### Interactive Patent Trends")
            st.info("Interactive visualization available - open in browser for full interactivity")
        
        if (reports_dir / "interactive_inventors.html").exists():
            st.markdown("#### Interactive Inventor Analysis")
            st.info("Interactive visualization available - open in browser for full interactivity")
        
        if (reports_dir / "patent_report.json").exists():
            st.markdown("#### Patent Report Summary")
            with open(reports_dir / "patent_report.json", "r") as f:
                import json
                report = json.load(f)
                st.json(report)

if __name__ == "__main__":
    main()