"""
UK Salary vs Cost of Living Pipeline
=====================================
Pulls live salary data from ONS ASHE and rent data from ONS PIPR.
Calculates disposable income after UK tax, NI, rent, and transport
for 10 UK cities. Loads results into SQLite for Power BI connection.

Usage: python main.py
"""

import os
import pandas as pd

from src.extract_salary import extract_salaries
from src.extract_rent   import extract_rents
from src.transform      import transform, generate_salary_scenarios
from src.load           import load_all


def run_pipeline() -> None:
    print("=" * 60)
    print("  UK SALARY VS COST OF LIVING — DATA PIPELINE")
    print("=" * 60)
    
    # Create output directories
    os.makedirs("data/raw",       exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("database",       exist_ok=True)
    
    # EXTRACT
    print("\n[1/4] EXTRACTING salary data from ONS ASHE...")
    salaries = extract_salaries()
    
    print("\n[2/4] EXTRACTING rent data from ONS PIPR...")
    rents = extract_rents()
    
    # TRANSFORM
    print("\n[3/4] TRANSFORMING — calculating disposable income...")
    summary   = transform(salaries, rents)
    scenarios = generate_salary_scenarios(rents)
    
    # Save processed CSVs (for Power BI connection)
    summary.to_csv("data/processed/disposable_income.csv", index=False)
    scenarios.to_csv("data/processed/salary_scenarios.csv", index=False)
    print("\nProcessed CSVs saved to data/processed/")
    
    # LOAD
    print("\n[4/4] LOADING to SQLite database...")
    load_all(summary, scenarios)
    
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  Database:  database/uk_cost_of_living.db")
    print(f"  CSV files: data/processed/")
    print(f"\nNext step: Connect Power BI Desktop to the CSV files")
    print(f"  File: data/processed/disposable_income.csv")
    print(f"  File: data/processed/salary_scenarios.csv")


if __name__ == "__main__":
    run_pipeline()