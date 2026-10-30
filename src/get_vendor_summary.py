import logging
import os
import sqlite3
import pandas as pd
from ingestion_db import ingest_db

# Ensure the 'logs' directory exists so the log file can be written successfully
os.makedirs("logs", exist_ok=True)

# Place logging configuration at the very top
logging.basicConfig(
    filename="logs/get_vendor_summary.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
    force=True,  # Overrides any logger initialized by imported packages
)


def create_vendor_summary(conn):
  """This function will merge the different table to get the overall vendor summary and adding the new columns in the resultant data"""
  Summerize_query = """
    WITH FreightSummary AS (
        SELECT 
            VendorNumber,
            SUM(Freight) AS Freight_cost 
        FROM vendor_invoice 
        GROUP BY VendorNumber
    ),
    PurchaseSummary AS (
        SELECT 
            p.VendorNumber,
            p.VendorName,
            p.Brand,
            p.Description,
            p.PurchasePrice,
            pp.Volume,
            pp.Price AS ActualPrices,
            SUM(p.Quantity) AS TotalPurchaseQuantity,
            SUM(p.Dollars) AS TotalDollarsQuantity 
        FROM purchases p 
        JOIN purchase_prices pp ON p.Brand = pp.Brand
        WHERE p.PurchasePrice > 0
        GROUP BY p.VendorNumber, p.VendorName, p.Brand, p.Description, p.PurchasePrice, pp.Volume, pp.Price
    ),
    SalesSummary AS (
        SELECT 
            VendorNO,
            Brand,
            SUM(SalesDollars) AS TotalSalesDollars,
            SUM(SalesPrice) AS TotalSalesPrice,
            SUM(SalesQuantity) AS TotalSalesQuantity,
            SUM(ExciseTax) AS TotalExciseTax
        FROM sales
        GROUP BY VendorNO, Brand
    )
    SELECT
        ps.VendorNumber,
        ps.VendorName,
        ps.Brand,
        ps.Description,
        ps.PurchasePrice,
        ps.Volume,
        ps.ActualPrices,
        ps.TotalPurchaseQuantity,
        ps.TotalDollarsQuantity,
        ss.TotalSalesDollars,
        ss.TotalSalesPrice,
        ss.TotalSalesQuantity,
        ss.TotalExciseTax,
        fs.Freight_cost
    FROM PurchaseSummary ps
    LEFT JOIN SalesSummary ss
        ON ps.VendorNumber = ss.VendorNO
        AND ps.Brand = ss.Brand
    LEFT JOIN FreightSummary fs
        ON ps.VendorNumber = fs.VendorNumber
    ORDER BY ps.TotalDollarsQuantity DESC
    """

  vendor_sales_summary = pd.read_sql_query(Summerize_query, conn)
  return vendor_sales_summary


def clean_data(df):
  """This function will clean the data"""
  # fill missing values with 0
  df.fillna(0, inplace=True)

  # changing the datatype to float
  df["Volume"] = df["Volume"].astype("float64")

  # remove spaces from categorical columns
  df["VendorName"] = df["VendorName"].str.strip()
  df["Description"] = df["Description"].str.strip()

  # creating more columns for better analysis
  df["GrossProfit"] = df["TotalSalesDollars"] - df["TotalDollarsQuantity"]

  # Correct Profit Margin Formula: (Gross Profit / Revenue) * 100
  df["ProfitMargin"] = (
      df["GrossProfit"] / df["TotalSalesDollars"].replace(0, 1)
  ) * 100
  df["StockTurnover"] = df[
      "TotalSalesQuantity"
  ] / df["TotalPurchaseQuantity"].replace(0, 1)
  df["SalesToPurchseRatio"] = df["TotalSalesDollars"] / df[
      "TotalDollarsQuantity"
  ].replace(0, 1)

  return df


if __name__ == "__main__":
  conn = sqlite3.connect("inventory.db")

  logging.info("Creating the Vendor Summary Table .....")
  summary_df = create_vendor_summary(conn)
  logging.info("\n%s", summary_df.head().to_string())

  logging.info("Cleaning Data ...")
  clean_df = clean_data(summary_df)
  logging.info("\n%s", clean_df.head().to_string())

  logging.info("Ingesting Data ....")
  ingest_db(clean_df, "vendor_sales_summary", conn)
  logging.info("!!Completed!!")

  conn.close()