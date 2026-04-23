# Patent Intelligence Dashboard

A streamlined Streamlit web application for exploring USPTO patent data insights and trends.

## Features

- **📊 Interactive Dashboard**: Clean, modern interface with key patent visualizations
- **📈 Patent Trends**: Historical patent filing trends from 1976-2023
- **🏆 Top Contributors**: Leading inventors and companies by patent count
- **🌍 Global Distribution**: Patent distribution across countries
- **⚡ Lightweight**: No database dependencies, runs efficiently on Streamlit Cloud
- **📱 Responsive**: Optimized for web deployment

## Quick Start

### Online Demo

Visit the live dashboard at: [Streamlit Cloud URL]

### Local Development

```bash
git clone https://github.com/yourusername/patent-intelligence-dashboard.git
cd patent-intelligence-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
patent-intelligence-dashboard/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── app.py                 # Streamlit dashboard
├── sql/                   # Database schema (reference)
├── reports/               # Generated visualizations (optional)
└── notebooks/             # Jupyter analysis notebooks (optional)
```

## Key Insights Displayed

- **9.4M+ Patents** analyzed from USPTO database
- **Patent growth trends** showing exponential increase since 2000
- **Top 10 inventors** led by Shunpei Yamazaki (2,364 patents)
- **Top 10 companies** led by IBM (158K+ patents)
- **Global distribution** with 85% US dominance

## Technology Stack

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

## Deployment

The app is optimized for Streamlit Cloud deployment with:

- ✅ Under 100MB resource usage
- ✅ No external database dependencies
- ✅ Pre-computed data for fast loading
- ✅ Responsive design for all devices

````

This will:

- Extract and clean the USPTO data
- Create the SQLite database
- Run analysis queries
- Generate reports

### 5. Run Analysis Separately

If the database already exists, run analysis only:

```bash
python run_analysis.py
````

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
