import logging
import os
import time
import pandas as pd
from sqlalchemy import create_engine

# Ensure the 'logs' folder exists
os.makedirs("logs", exist_ok=True)

# Configure logging settings (fixed formatting syntax)
logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
)

# FIXED: Corrected spelling to match 'inventory.db'
engine = create_engine("sqlite:///inventory.db")


def ingest_db(df, table_name, engine):
  df.to_sql(
      table_name,
      con=engine,
      if_exists="replace",
      index=False,
      chunksize=10000,
  )


def load_raw_data():
  start = time.time()

  # Check if data directory exists first
  if not os.path.exists("data"):
    print("Error: 'data' folder not found in current directory!")
    return

  for file in os.listdir("data"):
    if file.endswith(".csv"):
      file_path = os.path.join("data", file)
      df = pd.read_csv(file_path)

      # Extract table name safely without extension (.csv)
      table_name = os.path.splitext(file)[0]

      logging.info(f"Ingesting {file} into table '{table_name}'")
      ingest_db(df, table_name, engine)

  end = time.time()
  final_time = (end - start) / 60
  logging.info("Ingestion complete")
  logging.info(f"Total Time Taken: {final_time:.2f} minutes")
  print("Data ingestion completed successfully!")


# FIXED: Actually call the function to run the script!
if __name__ == "__main__":
  load_raw_data()