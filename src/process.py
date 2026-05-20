import pandas as pd
from pydantic import ValidationError
import logging
import os
import sys

# Add the root directory to the python path so we can import our models easily
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models import CommodityTrade

# Set up professional logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_trade_blotter(file_path: str):
    logging.info(f"Loading raw blotter from {file_path}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        logging.error(f"Failed to read file: {e}")
        return None, None

    clean_trades = []
    quarantined_trades = []

    for index, row in df.iterrows():
        row_dict = row.to_dict()
        
        # Pandas puts NaNs for empty cells, which breaks Pydantic. 
        # Convert NaNs to None for cleaner validation.
        row_dict = {k: (v if pd.notna(v) else None) for k, v in row_dict.items()}

        try:
            # 1. Validate the row against our strict schema
            valid_trade = CommodityTrade(**row_dict)
            
            # 2. Calculate Notional Value (The Business Logic)
            # .model_dump() safely converts the pydantic object back to a dictionary
            trade_data = valid_trade.model_dump()
            trade_data['Notional_Value_USD'] = trade_data['Volume_MMBtu'] * trade_data['Price_USD']
            
            clean_trades.append(trade_data)
            
        except ValidationError as e:
            # 3. Catch bad data, extract the error reason, and quarantine it
            # We flatten the error message so it fits nicely in a CSV cell
            error_msg = str(e).replace('\n', ' | ')
            row_dict['Validation_Error'] = error_msg
            quarantined_trades.append(row_dict)
            
    logging.info(f"Processed {len(df)} rows.")
    logging.info(f"Clean Trades: {len(clean_trades)}")
    logging.warning(f"Quarantined Trades: {len(quarantined_trades)}")
    
    return pd.DataFrame(clean_trades), pd.DataFrame(quarantined_trades)

from sqlalchemy import create_engine

if __name__ == "__main__":
    # 1. Run the ingestion and validation
    raw_file_path = "data/raw_blotter.xlsx"
    clean_df, bad_df = process_trade_blotter(raw_file_path)
    
    # 2. Quarantine bad data
    if bad_df is not None and not bad_df.empty:
        quarantine_path = "data/outputs/quarantined_trades.csv"
        bad_df.to_csv(quarantine_path, index=False)
        logging.info(f"Saved quarantined trades to {quarantine_path}")
        
    # 3. Push clean data to Database
    if clean_df is not None and not clean_df.empty:
        db_path = "sqlite:///data/trading_data.db"
        engine = create_engine(db_path)
        
        # Write to SQL (replace table if it exists for this daily run)
        clean_df.to_sql('daily_trades', con=engine, if_exists='replace', index=False)
        logging.info(f"Successfully pushed {len(clean_df)} trades to SQLite database.")