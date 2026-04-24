from src.transform import calc_income_tax, calc_national_insurance, calc_monthly_takehome

def test_no_tax_below_personal_allowance():
    assert calc_income_tax(12_000) == 0.0

def test_basic_rate_tax():
    # £30k: taxable = 17,430 x 20% = 3,486
    assert calc_income_tax(30_000) == 3_486.0

def test_monthly_takehome_reasonable_for_35k():
    takehome = calc_monthly_takehome(35_000)
    assert 2_200 < takehome < 2_500

def test_no_ni_below_threshold():
    assert calc_national_insurance(12_000) == 0.0

def test_higher_salary_gives_higher_takehome():
    assert calc_monthly_takehome(60_000) > calc_monthly_takehome(40_000)