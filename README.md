# Commodity Trade Reconciliation Pipeline

[![Trade Pipeline CI](https://github.com/ArsenKh-UoA/commodity-trade-reconciliation/actions/workflows/ci.yml/badge.svg)](https://github.com/ArsenKh-UoA/commodity-trade-reconciliation/actions/workflows/ci.yml)

A decoupled ETL and risk-reporting pipeline for commodity trade data, built with Python, pandas, and SQLite.

## Project Context & Scope
This repository is designed as a portfolio demonstration of a decoupled ETL and risk-reporting architecture. 

* **Synthetic Data:** The `raw_blotter.xlsx` file contains programmatically generated mock data designed to simulate an internal end-of-day desk blotter. It does not contain real market data, nor does it represent actual exchange logs.
* **Current Scope (Ingestion Governance):** This iteration focuses on strict boundary-layer validation (Pydantic) and data persistence (SQLite) to guarantee internal state integrity.
* **Future Scope (External Reconciliation):** Stateful reconciliation—such as matching internal database records against simulated ICE/CME clearing reports to identify economic breaks or duplicates—is scoped for a future build.

## The Business Problem
Commodity trading desks often rely on manual, error-prone Excel spreadsheets to track end-of-day PnL and risk metrics. Dirty data (missing prices, negative volumes, malformed strings) can silently corrupt risk reports, leading to operational bottlenecks and miscalculated exposure.

## The Solution
An automated, CI/CD-integrated Python pipeline that ingests raw trade blotters, rigorously sanitizes the data using strict schemas, persists it to a relational database, and generates reconciled end-of-day risk reports. 

### Architecture & Tech Stack
* **Data Ingestion & Aggregation:** `pandas`
* **Data Validation (Risk Controls):** `pydantic`
* **Persistence:** `sqlite3` + `SQLAlchemy` (ORM)
* **Testing & CI/CD:** `pytest` + GitHub Actions

## Pipeline Features
1. **Schema Validation:** Enforces strict typing (e.g., ensuring `Volume_MMBtu` and `Price_USD` are strictly positive floats) before data touches the database.
2. **Quarantine System:** Bad data is not dropped; it is caught, logged, and exported to a `quarantined_trades.csv` file for manual desk review.
3. **Decoupled Reporting:** A separate module queries the SQLite database to calculate Net Directional Volume and Gross Notional Exposure aggregated by Counterparty and Commodity Index (TTF, NBP, Henry Hub).

## Execution
```bash
# 1. Run the ingestion and database pipeline
python src/process.py

# 2. Generate the End-of-Day Risk Summary
python src/risk_report.py

# 3. Run the automated test suite
pytest tests/
