import pandas as pd
from sqlalchemy import create_engine
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def generate_risk_report():
    db_path = "sqlite:///data/trading_data.db"
    engine = create_engine(db_path)
    
    logging.info("Connecting to database and extracting daily trades...")
    try:
        # Read directly from the SQL database
        df = pd.read_sql("SELECT * FROM daily_trades", con=engine)
    except Exception as e:
        logging.error(f"Failed to read from database: {e}")
        return
        
    # BUSINESS LOGIC: Calculate Net Directional Volume
    # If we BUY, volume is positive. If we SELL, volume is negative.
    df['Net_Volume'] = df.apply(
        lambda row: row['Volume_MMBtu'] if row['Direction'] == 'BUY' else -row['Volume_MMBtu'], 
        axis=1
    )
    
    # Aggregate Risk by Counterparty and Commodity Index
    logging.info("Calculating End-of-Day Risk Exposures...")
    risk_summary = df.groupby(['Counterparty', 'Commodity_Index']).agg(
        Total_Trades=('Trade_ID', 'count'),
        Net_Volume_MMBtu=('Net_Volume', 'sum'),
        Gross_Notional_Exposure_USD=('Notional_Value_USD', 'sum')
    ).reset_index()
    
    # Format the Notional Exposure to look like currency for the Traders
    risk_summary['Gross_Notional_Exposure_USD'] = risk_summary['Gross_Notional_Exposure_USD'].apply(
        lambda x: f"${x:,.2f}"
    )
    
    # Save the report
    output_path = "data/outputs/End_of_Day_Risk_Summary.csv"
    risk_summary.to_csv(output_path, index=False)
    logging.info(f"Risk Report generated successfully: {output_path}")
    
    # Print a preview to the terminal so we look like a pro
    print("\n--- End of Day Risk Summary Preview ---")
    print(risk_summary.head().to_markdown(index=False))
    print("---------------------------------------\n")

if __name__ == "__main__":
    generate_risk_report()