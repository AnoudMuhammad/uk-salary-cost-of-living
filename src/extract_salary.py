import pandas as pd
import os

# The correct names as they appear in the ONS file
# (I inspected the actual file to find these exact spellings)
CITY_LA_MAP = {
    'London':     'London',
    'Manchester': 'Manchester',
    'Birmingham': 'Birmingham',
    'Leeds':      'Leeds',
    'Bristol':    'Bristol, City of',
    'Edinburgh':  'City of Edinburgh',
    'Newcastle':  'Newcastle upon Tyne',
    'Cardiff':    'Cardiff',
    'Sheffield':  'Sheffield',
    'Liverpool':  'Liverpool',
}

FILE_PATH = "data/raw/ashe_annual_pay.xlsx"


def extract_salaries() -> pd.DataFrame:
    """
    Read the ASHE Table 7.7a Excel file (Annual pay - Gross 2024)
    and extract the median annual salary for each of our 10 cities.

    The file has:
    - Sheet: 'Full-Time'
    - Row 4 (index) is the header row (header=4)
    - Column 'Description' contains area names
    - Column 'Median' contains median annual gross pay
    """
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(
            f"\nFile not found: {FILE_PATH}\n"
            "Please save the file 'Work Geography Table 7.7a Annual pay - Gross 2024.xlsx'\n"
            "from the zip into data/raw/ and rename it to ashe_annual_pay.xlsx"
        )

    print(f"Reading: {FILE_PATH}")

    # Read the Full-Time sheet, row 4 is the header
    df = pd.read_excel(FILE_PATH, sheet_name='Full-Time', header=4)

    # Clean up
    df = df[df['Description'].notna()].copy()
    df['Description'] = df['Description'].astype(str).str.strip()

    print(f"Loaded {len(df)} rows from Full-Time sheet")
    print("Extracting city data...\n")

    records = []

    for city, la_name in CITY_LA_MAP.items():
        # Find the row for this city
        mask  = df['Description'].str.contains(la_name, case=False, na=False)
        match = df[mask]

        if match.empty:
            print(f"  WARNING: '{la_name}' not found in file")
            continue

        # Get the median value — take the first match
        raw_val = match['Median'].iloc[0]

        try:
            salary = float(str(raw_val).replace(',', '').strip())

            records.append({
                'city':                 city,
                'local_authority':      la_name,
                'median_annual_salary': round(salary, 2),
                'salary_source':        'ONS ASHE Table 7.7a 2024'
            })

            print(f"  {city:<12}: £{salary:>8,.0f} / year")

        except (ValueError, TypeError):
            print(f"  WARNING: Could not parse value '{raw_val}' for {city}")

    result_df = pd.DataFrame(records)

    # Save so we can inspect it
    os.makedirs("data/raw", exist_ok=True)
    result_df.to_csv("data/raw/ashe_salaries.csv", index=False)
    print(f"\nSaved {len(result_df)} cities to data/raw/ashe_salaries.csv")

    return result_df


if __name__ == "__main__":
    df = extract_salaries()
    print("\n--- Final result ---")
    print(df.to_string(index=False))