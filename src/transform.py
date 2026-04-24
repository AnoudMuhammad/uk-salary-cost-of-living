import pandas as pd

PERSONAL_ALLOWANCE = 12_570
BASIC_RATE_LIMIT   = 50_270
HIGHER_RATE_LIMIT  = 125_140
NI_PRIMARY_THRESHOLD = 12_570
NI_UPPER_LIMIT       = 50_270

TRANSPORT_MONTHLY = {
    'London':     165,
    'Manchester':  75,
    'Birmingham':  70,
    'Leeds':       65,
    'Bristol':     72,
    'Edinburgh':   68,
    'Newcastle':   58,
    'Cardiff':     62,
    'Sheffield':   60,
    'Liverpool':   63,
}

def calc_income_tax(gross_annual: float) -> float:
    taxable = max(0.0, gross_annual - PERSONAL_ALLOWANCE)
    tax = 0.0
    basic_band = BASIC_RATE_LIMIT - PERSONAL_ALLOWANCE
    tax += min(taxable, basic_band) * 0.20
    if taxable > basic_band:
        higher_band = HIGHER_RATE_LIMIT - BASIC_RATE_LIMIT
        tax += min(taxable - basic_band, higher_band) * 0.40
    if taxable > (HIGHER_RATE_LIMIT - PERSONAL_ALLOWANCE):
        tax += (taxable - (HIGHER_RATE_LIMIT - PERSONAL_ALLOWANCE)) * 0.45
    return round(tax, 2)

def calc_national_insurance(gross_annual: float) -> float:
    if gross_annual <= NI_PRIMARY_THRESHOLD:
        return 0.0
    ni = 0.0
    main_band = min(gross_annual, NI_UPPER_LIMIT) - NI_PRIMARY_THRESHOLD
    ni += main_band * 0.12
    if gross_annual > NI_UPPER_LIMIT:
        ni += (gross_annual - NI_UPPER_LIMIT) * 0.02
    return round(ni, 2)

def calc_monthly_takehome(gross_annual: float) -> float:
    tax = calc_income_tax(gross_annual)
    ni  = calc_national_insurance(gross_annual)
    return round((gross_annual - tax - ni) / 12, 2)

def transform(salaries: pd.DataFrame, rents: pd.DataFrame) -> pd.DataFrame:
    df = salaries.merge(rents, on='city', how='inner')
    df['monthly_takehome']    = df['median_annual_salary'].apply(calc_monthly_takehome)
    df['monthly_transport']   = df['city'].map(TRANSPORT_MONTHLY)
    df['monthly_disposable']  = (df['monthly_takehome'] - df['median_monthly_rent'] - df['monthly_transport']).round(2)
    df['rent_pct_takehome']   = (df['median_monthly_rent'] / df['monthly_takehome'] * 100).round(1)
    df['annual_savings']      = (df['monthly_disposable'] * 12).round(2)
    df['rent_over_30pct']     = df['rent_pct_takehome'] > 30
    df['disposable_rank']     = df['monthly_disposable'].rank(ascending=False).astype(int)

    print("\n=== RESULTS ===")
    print(f"{'Rank':<5} {'City':<12} {'Salary':>8} {'Take-home':>10} {'Rent':>8} {'Disposable':>11} {'Rent%':>6}")
    print("-" * 65)
    for _, row in df.sort_values('disposable_rank').iterrows():
        flag = " !" if row['rent_over_30pct'] else ""
        print(
            f"  {row['disposable_rank']:<4}"
            f"{row['city']:<12}"
            f"£{row['median_annual_salary']:>7,.0f}"
            f"  £{row['monthly_takehome']:>7,.0f}"
            f"  £{row['median_monthly_rent']:>5,.0f}"
            f"  £{row['monthly_disposable']:>7,.0f}"
            f"  {row['rent_pct_takehome']:>5.0f}%{flag}"
        )
    return df

def generate_salary_scenarios(rents: pd.DataFrame) -> pd.DataFrame:
    records = []
    for city in TRANSPORT_MONTHLY.keys():
        city_rent = rents[rents['city'] == city]
        if city_rent.empty:
            continue
        monthly_rent = city_rent['median_monthly_rent'].iloc[0]
        transport    = TRANSPORT_MONTHLY[city]
        for salary in range(20_000, 105_000, 5_000):
            takehome   = calc_monthly_takehome(salary)
            disposable = takehome - monthly_rent - transport
            records.append({
                'city':               city,
                'gross_salary':       salary,
                'monthly_takehome':   round(takehome, 2),
                'monthly_rent':       monthly_rent,
                'monthly_transport':  transport,
                'monthly_disposable': round(disposable, 2),
                'rent_pct_takehome':  round(monthly_rent / takehome * 100, 1),
                'annual_savings':     round(disposable * 12, 2),
            })
    df = pd.DataFrame(records)
    print(f"\nGenerated {len(df)} salary scenario rows")
    return df

if __name__ == "__main__":
    sal  = pd.read_csv("data/raw/ashe_salaries.csv")
    rent = pd.read_csv("data/raw/pipr_rents.csv")
    out  = transform(sal, rent)
    scen = generate_salary_scenarios(rent)
    import os; os.makedirs("data/processed", exist_ok=True)
    out.to_csv("data/processed/disposable_income.csv", index=False)
    scen.to_csv("data/processed/salary_scenarios.csv", index=False)
    print("\nSaved to data/processed/")