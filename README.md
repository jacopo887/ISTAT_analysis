# Road Accidents in Italy – Where to Invest in Road Safety?

Data Analytics capstone project (Boolean).

**Business question:** a company working in road traffic management and risk prevention wants to know which Italian municipalities are the best candidates for investment, based on accident rates, totals, population and territory.

## Data sources
- **ISTAT** – road accidents with injuries, killed and injured by municipality, 2015–2024 (SDMX API, dataflow `41_983`), downloaded automatically in chunks of years, with local cache and rate-limit handling.
- **SITUAS** – population and area (km²) of all municipalities at 31/12/2020, scraped with **Selenium** (report 74).

## Project structure
```
├── utilities.py        # data download (ISTAT API, SITUAS scraping) and export for Power BI
├── notebook.ipynb      # full analysis
├── data/
│   ├── raw/            # downloaded data (ISTAT chunks + metadata, SITUAS csv)
│   └── processed/      # clean data and csv files used in Power BI
├── dashboard.pbix      # Power BI dashboard
└── presentation.pdf    # project deck
```

## Analysis steps
1. **Data fetching** – ISTAT API + SITUAS scraping
2. **First look** – structure, data types, missing values, meaning of the codes (from the ISTAT metadata)
3. **Cleaning & join** – codes as text, long → wide table, missing zeros in 2024, join with population and area
4. **EDA** – national trend, distributions, outliers, geographical comparison, correlations
5. **New columns** – accidents per 1,000 inhabitants, per km², killed per 100 accidents, combined investment score
6. **Clustering** – K-Means on risk metrics (4 profiles)
7. **Hypothesis test** – Centre-North vs South accident rate (permutation test + t-test)
8. **Regression & forecast** – OLS on accident rate drivers, national trend forecast 2025–2027
9. **Export** – csv files for the Power BI dashboard

## Main findings
- Accidents are **stable** at ~170k per year (−31% in 2020 due to COVID), while **killed and injured are decreasing**.
- Absolute numbers mostly reflect city size: municipalities are compared with **rates**, keeping only those with ≥ 10,000 inhabitants.
- The **Centre-North** has a significantly higher accident rate than the South (2.88 vs 2.01 per 1,000 inhabitants), also controlling for size and density.
- **"Urban hotspots"** (128 municipalities) account for **half of all accidents** → highest-impact investment targets (e.g. Florence, Bergamo, Genoa, Milan, Bologna).

## How to run
```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels scikit-learn requests beautifulsoup4 lxml selenium
```
Open `notebook.ipynb` from the project folder and run all cells. Downloads are cached in `data/raw/`: if the files already exist, the APIs are not called again. The SITUAS scraping requires Google Chrome.

## Limits
- Population and area refer to 2020 for all years; tourist towns have rates inflated by non-resident traffic.
- ISTAT data include only accidents with injuries recorded by the police.
- The forecast is a simple linear trend on 8 yearly values.

## Author
Jacopo Sinigaglia
