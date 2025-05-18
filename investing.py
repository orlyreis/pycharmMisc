# This is a sample Python script.
import numpy as np
import yfinance as yf
import investpy
import requests
import pandas as pd
from bcb import sgs
from datetime import datetime
import matplotlib.pyplot as plt

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

financial_params = dict(yearly_interest=0.140830823529, yearly_inflation=0.059171235294, time_length_year=100, age_of_contribution_year=28,
                        contribution_length_year=17, income_age_year=50, passive_income_value=8000,
                        contribution_value=100, reference_year=2008, reference_month=1, birth_year=1980, birth_month=8)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def assets_projection(financial_params):
    yearly_interest = financial_params['yearly_interest']
    yearly_inflation = financial_params['yearly_inflation']
    time_length_year = financial_params['time_length_year']
    age_of_contribution_year = financial_params['age_of_contribution_year']
    contribution_length_year = financial_params['contribution_length_year']
    income_age_year = financial_params['income_age_year']
    contribution_value = financial_params['contribution_value']
    passive_income_value = financial_params['passive_income_value']
    reference_year = financial_params['reference_year']
    birth_year = financial_params['birth_year']

    age_of_contribution = age_of_contribution_year * 12
    contribution_length = contribution_length_year * 12
    income_age = income_age_year * 12
    monthly_interest = (1 + yearly_interest) ** (1 / 12) - 1
    time_length = time_length_year * 12
    Accumulated_amount: list[float] = time_length * [float(0)]

    while Accumulated_amount[-1] < 1:

        contribution_value = contribution_value + .1

        #clear the list
        capital_contribution = age_of_contribution * [float(0)] + contribution_length * [float(0)] + (
                    time_length - contribution_length - age_of_contribution) * [float(0)]

        # Adding the contribution value for the first year
        capital_contribution[age_of_contribution_year * 12: age_of_contribution_year * 12 + 12] = 12 * [
            contribution_value]

        # it will add the next contributions with the inflation adjustment
        for i in range(age_of_contribution_year + 1, age_of_contribution_year + contribution_length_year):
            capital_contribution[i * 12:i * 12 + 12] = 12 * [
                round(capital_contribution[12 * i - 1] * (1 + yearly_inflation), 2)]

        #clear the list
        passive_income = (time_length - income_age) * [float(0)] + income_age * [0]

        # The value of first year of passive income is correct by inflation from the age of contribution to the age of retirement
        passive_income[12 * income_age_year:12 * income_age_year + 12] = 12 * [round(
            float(passive_income_value * (1 + yearly_inflation) ** (income_age_year - (reference_year - birth_year))),
            2)]
        for j in range(income_age_year + 1, time_length_year):
            passive_income[j * 12:j * 12 + 12] = 12 * [round(passive_income[12 * j - 1] * (1 + yearly_inflation), 2)]

        # clear the list
        Accumulated_amount = time_length * [float(0)]
        # the first mount is yield
        Accumulated_amount[0] = (capital_contribution[0]) * (1 + monthly_interest)

        # A new interest is taken from the new contribution, the previous accumulated amount and from the subtraction from the passive income for the next months
        for i in range(1, time_length):
            Accumulated_amount[i] = (capital_contribution[i] + Accumulated_amount[i - 1] - passive_income[i]) * (
                        1 + monthly_interest)

    return capital_contribution, passive_income, Accumulated_amount


def get_investing_assets(country, asset_type):
    assets_list = []
    try:
        if asset_type == 'funds':
            assets_list = investpy.funds.get_funds(
                country)  #https://investpy.readthedocs.io/_api/funds.html
        elif asset_type == 'stocks':
            assets_list = investpy.stocks.get_stocks(
                country)  #https://investpy.readthedocs.io/_api/funds.html
    except:
        print(f'Wrong country: {country}')
        return None
    else:
        # Chamar a função para ler o arquivo
        print(f'Fetching {asset_type} list from {country}')
        symbol_list = list(assets_list['symbol'])
        return symbol_list


def annual_mean_inflation(start_year, code):
    #Indicador	Código BCB
    #IPCA	433
    #IGPM (FGV)	189
    #Selic	11
    today = datetime.now().strftime("%y-%m-%d")
    if code == "IGPM":
        inflation = sgs.get({"IGPM": 189}, start=start_year)
    elif code == "IPCA":
        inflation = sgs.get({"IPCA": 433}, start=start_year)
    elif code == "Selic":
        inflation = sgs.get({"Selic": 11}, start=start_year)
    else:
        print("Wrong code")
        return None

    # geometric mean with logarithmic approach

    geo_mean = np.array([])
    for year in range(int(start_year[0:4]), int(datetime.now().strftime("%Y"))):
        yearly_rate = np.array([])
        for i in range(0, 12):
            yearly_rate = np.append(yearly_rate, 1 + inflation.loc[str(year)][code].iloc[i]/100)
        yearly_rate = np.prod(yearly_rate)
        geo_mean = np.append(geo_mean, yearly_rate)
    geo_mean = np.exp(np.mean(np.log(geo_mean))) - 1

    return geo_mean




if __name__ == '__main__':
    print_hi('PyCharm')



# assets_list = get_investing_assets('sweden', 'funds')
#
# search_results = yf.Search('0P0001Q6FG.ST')
# info = search_results.all
#
# symbol_yf = info['quotes'][0]['symbol']
# date_start = '2023-01-03'
# date_end = "2025-01-03"
# data = yf.download(symbol_yf, start=date_start, end=date_end)
# print(data.head())
# valor = data.loc[date_start, 'Close'].iloc[0]
# print(valor)
# print(data.tail)

reference_date = dict(year = 2008, month = 8)

IGPM = annual_mean_inflation(f"{reference_date['year']}-01-01","IGPM")
Selic = annual_mean_inflation("2024-04-01","Selic")
print(f"Mean inflation IGPM: {IGPM}")
print(f"Mean inflation SELIC: {Selic}")
itau = (1+IGPM)*(1+0.06) - 1
print(f"Mean yield IGPM+6: {itau}")

financial_params['yearly_inflation'] = annual_mean_inflation(f"{reference_date['year']}-01-01","IPCA")
financial_params['reference_year'] = reference_date['year']

print(f"Mean inflation IPCA: {financial_params['yearly_inflation']}")
capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params)

# It save the lists in a excell file.
df = pd.DataFrame(list(zip(capital_contribution, passive_income, [round(p, 2) for p in Accumulated_amount])), columns=["Capital_contribution","passive_income","Accumulated_amount"])
df.to_excel("invest.xlsx", index=False)  # Remove `index=False` to keep row numbers

years = [i * 0.5 for i in range(0, 200)]
plt.plot(years, Accumulated_amount[0:1200:6], label='Amount of saving #1', color='red')
plt.plot(years, passive_income[0:1200:6], label='Passive incomes #1', color='red')
#plt.plot(years, capital_contribution[0:1200:6], label='Passive incomes #1', color='red')
plt.title('Yield Projection (2024)')
plt.xlabel('Month')
plt.ylabel('Value (BRL)')
plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
