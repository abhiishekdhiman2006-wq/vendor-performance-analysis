# Vendor Performance Analysis

Analysis of vendor, brand, pricing and inventory performance for a beverage distributor, using Python, SQLite and a dashboard.

## Project structure
| Path | Description |
|---|---|
| `src/ingestion_db.py` | Loads every CSV in `data/` into the SQLite database `inventory.db` (with logging). |
| `src/get_vendor_summary.py` | Builds the `vendor_sales_summary` table (SQL joins, cleaning, GrossProfit, ProfitMargin, StockTurnover, SalesToPurchaseRatio). |
| `notebooks/Exploratory_Data_Analysis.ipynb` | Explores the source tables and designs the summary query. |
| `notebooks/vendor_perfromance_analysis.ipynb` | Cleaning, plots, business questions, confidence intervals and t-test. |
| `report/` | Full project report (Word and PDF). |
| `dashboard/` | Dashboard images and the web dashboard. |
| `images/` | Plots exported from the notebook. |

## How to run
1. Put the raw CSV files in a `data/` folder (not included in this repo).
2. `pip install pandas sqlalchemy matplotlib seaborn scipy`
3. `python src/ingestion_db.py`
4. `python src/get_vendor_summary.py`
5. Open the notebooks in `notebooks/` and run them.

## Key results
- Top 10 vendors account for 65.69% of purchase dollars.
- Large orders have about 72% lower unit price than small orders.
- About $2.71M is locked in unsold inventory.
- Low-sales vendors earn higher margins (41.57%) than top-sales vendors (31.18%); Welch t-test p < 0.001.

## Data
Raw CSV files and `inventory.db` are excluded because of GitHub's file-size limit.
