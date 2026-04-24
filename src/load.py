import pandas as pd
from sqlalchemy import create_engine, text
import os


DB_PATH = "database/uk_cost_of_living.db"


def get_engine():
    """Create and return a SQLAlchemy engine connected to SQLite."""
    os.makedirs("database", exist_ok=True)
    return create_engine(f"sqlite:///{DB_PATH}")


def load_to_sqlite(df: pd.DataFrame, table_name: str) -> None:
    """
    Load a pandas DataFrame into a SQLite table.
    
    if_exists='replace' means: if the table already exists,
    drop it and recreate it with fresh data.
    This is fine for our pipeline — we always want the latest data.
    """
    engine = get_engine()
    
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',
        index=False
    )
    
    # Verify the load worked by counting rows
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    
    print(f"  Loaded {count} rows into table '{table_name}'")


def load_all(summary_df: pd.DataFrame, scenarios_df: pd.DataFrame) -> None:
    """Load both DataFrames into their respective tables."""
    print(f"\nLoading to SQLite: {DB_PATH}")
    load_to_sqlite(summary_df,   "city_income_summary")
    load_to_sqlite(scenarios_df, "salary_scenarios")
    print(f"Database ready at: {DB_PATH}")
    print("Tip: Open this file with DB Browser for SQLite to inspect it")


if __name__ == "__main__":
    # Quick test — create a dummy DataFrame and load it
    test_df = pd.DataFrame({
        'city': ['London', 'Manchester'],
        'test_value': [100, 200]
    })
    load_to_sqlite(test_df, "test_table")
    print("Load test passed!")