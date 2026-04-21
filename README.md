# Patent Intelligence Data Pipeline

A comprehensive, reproducible patent data analysis system that processes USPTO bulk patent data, builds a relational database, and generates insights on inventors, companies, and patent trends.

## Features

- **Data Processing**: Downloads and processes USPTO bulk patent data (9.4M+ patents)
- **Database**: SQLite relational database with optimized schema and indexes
- **Analysis**: SQL queries for top inventors, companies, countries, and trends
- **Reports**: Console, CSV, and JSON output formats
- **Visualizations**: Static and interactive graphs and charts (matplotlib, seaborn, plotly)
- **Dashboard**: Streamlit web application for interactive data exploration
- **Advanced Analysis**: Patent category analysis and complexity trends
- **Reproducible**: Complete setup with Git version control and dependency management

## Project Structure

```
patent-pipeline/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── patent_pipeline.py        # Main data processing pipeline
├── run_analysis.py           # Analysis and reporting script
├── create_visualizations.py  # Data visualization script
├── app.py                    # Streamlit dashboard
├── analyze_categories.py     # Advanced patent category analysis
├── sql/
│   ├── schema.sql           # Database schema
│   └── queries.sql          # Sample SQL queries
├── data/                    # Data files (not in repo - see setup)
├── reports/                 # Generated reports and visualizations
│   ├── *.png                # Static charts
│   ├── *.html               # Interactive charts
│   ├── *.csv                # Data exports
│   └── *.json               # JSON reports
└── notebooks/               # Jupyter notebooks for exploration
```

## Setup and Installation

### Prerequisites

- Python 3.12+
- Git
- Internet connection for data download

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/patent-pipeline.git
cd patent-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download USPTO Data

The project uses USPTO PatentsView bulk data. Download the following files and place them in the `data/` directory:

**Required Files:**

- `g_patent.tsv.zip` (Patent data)
- `g_inventor_disambiguated.tsv.zip` (Inventor data)
- `g_assignee_disambiguated.tsv.zip` (Assignee/Company data)

**Optional for Enhanced Analysis:**

- `g_cpc_current.tsv.zip` (Patent categories - CPC classifications)

Download from: https://patentsview.org/download/

**Note:** These are large files (~10GB total). The pipeline will automatically extract and process them.

### 4. Run the Pipeline

Execute the complete pipeline:

```bash
python patent_pipeline.py
```

This will:

- Extract and clean the USPTO data
- Create the SQLite database
- Run analysis queries
- Generate reports

### 5. Run Analysis Separately

If the database already exists, run analysis only:

```bash
python run_analysis.py
```

### 6. Create Visualizations

Generate interactive charts and graphs:

```bash
python create_visualizations.py
```

### 7. Launch Dashboard

Start the Streamlit web application:

```bash
streamlit run app.py
```

### 8. Advanced Category Analysis

Analyze patent categories and classifications:

```bash
python analyze_categories.py
```

## Outputs

### Database

- `data/patent_pipeline.db` - SQLite database (3.9GB)

### Reports

- `reports/top_inventors.csv` - Top 10 inventors by patent count
- `reports/top_companies.csv` - Top 10 companies by patent count
- `reports/top_countries.csv` - Patent distribution by country
- `reports/country_trends.csv` - Patent filings by year
- `reports/patent_report.json` - Complete structured report

### Visualizations

- `reports/patent_trends.png` - Patent filing trends over time
- `reports/top_inventors_chart.png` - Inventor patent distribution
- `reports/company_analysis.png` - Company patent analysis
- `reports/country_distribution.png` - Patent distribution by country
- `reports/patent_counts_by_year.png` - Patent counts by year (2010-2023)
- `reports/top_countries_basic.png` - Top countries by inventor count
- Interactive HTML charts: `interactive_trends.html`, `interactive_inventors.html`, `interactive_companies.html`
- Streamlit dashboard at `http://localhost:8501` for interactive exploration

## Key Findings

- **Total Patents**: 9,454,161
- **Top Inventor**: Shunpei Yamazaki (6,753 patents)
- **Top Company**: Samsung Display Co., Ltd. (174,536 patents)
- **Most Patents**: From unknown/unspecified countries (8.4M)

## Technical Details

- **Data Processing**: Chunked TSV reading for memory efficiency
- **Database**: SQLite with foreign keys and optimized indexes
- **Analysis**: SQL queries with JOINs, GROUP BY, and window functions
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Dashboard**: Streamlit for interactive exploration

## Reproducibility

This project is fully reproducible:

1. All code is version-controlled in Git
2. Dependencies are pinned in `requirements.txt`
3. Data sources are publicly available from USPTO
4. Scripts handle data download, processing, and analysis automatically
5. Results are deterministic given the same input data

Anyone can clone this repository, run the setup steps, and reproduce the exact same results.

## License

This project uses public USPTO data. See USPTO terms of use for data licensing.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
