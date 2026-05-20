import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

n_rows = 60
start_date = datetime(2026, 5, 1)

# Generate realistic commodity trade fields
trade_ids = [f"TRD-{1000 + i}" for i in range(n_rows)]
dates = [(start_date + timedelta(days=int(i//2))).strftime("%Y-%m-%d") for i in range(n_rows)]
indices = np.random.choice(["TTF", "NBP", "Henry Hub"], size=n_rows)
counterparties = np.random.choice(["BP", "Shell", "Trafigura", "Vitol", "Glencore"], size=n_rows)
directions = np.random.choice(["BUY", "SELL"], size=n_rows)
volumes = np.random.randint(5000, 50000, size=n_rows)  # MMBtu
prices = np.round(np.random.uniform(2.5, 12.0, size=n_rows), 2)  # USD/MMBtu

df = pd.DataFrame({
    "Trade_ID": trade_ids,
    "Date": dates,
    "Commodity_Index": indices,
    "Counterparty": counterparties,
    "Direction": directions,
    "Volume_MMBtu": volumes,
    "Price_USD": prices
})

# --- INTENTIONAL ERRORS TO SIMULATE Messy Excel Processes ---
# --- INTENTIONAL ERRORS TO SIMULATE Messy Excel Processes ---
df.loc[5, "Price_USD"] = np.nan          # Missing price (Critical error)
df.loc[12, "Volume_MMBtu"] = -10500     # Negative volume (Anomaly)
df.loc[22, "Date"] = "CORRUPT_DATE"     # Malformed date string (Format issue)
df.loc[35, "Counterparty"] = None       # Missing counterparty

# FIX: Explicitly cast the column to 'object' so it allows mixed types (like an Excel column)
df["Price_USD"] = df["Price_USD"].astype(object)
df.loc[42, "Price_USD"] = "TEN"          # Text inside a numeric column (Type issue)

# Save to the data directory
df.to_excel("data/raw_blotter.xlsx", index=False)
print("Successfully generated data/raw_blotter.xlsx with intentional errors!")

