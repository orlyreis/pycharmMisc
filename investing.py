# This is a sample Python script.
import numpy as np
import yfinance as yf
import investpy
import pandas as pd
from bcb import sgs
from datetime import datetime
import matplotlib.pyplot as plt
import time

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

financial_params = dict(yearly_interest=0.13499942436095425, yearly_inflation=0.059171235294, time_length_year=100, age_of_contribution_year=28,
                        contribution_length_year=20, income_age_year=50, passive_income_value=8000,
                        contribution_value=1000, reference_year=2025, reference_month=1, birth_year=1980, birth_month=8)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def assets_projection(financial_params, file_name, refresh=False):
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

        contribution_value = contribution_value + 1
        print(Accumulated_amount[-1])
        #clear the list
        if refresh:
            capital_contribution = age_of_contribution * [float(0)] + contribution_length * [float(0)] + (
                    time_length - contribution_length - age_of_contribution) * [float(0)]

            # Adding the contribution value for the first year
            capital_contribution[age_of_contribution_year*12: age_of_contribution_year*12+12] = 12 * [contribution_value]

            # it will add the next contributions with the inflation adjustment
            for i in range(age_of_contribution_year+1, age_of_contribution_year + contribution_length_year):
                capital_contribution[i*12:i*12+12] = 12*[capital_contribution[12*i-1]*(1+yearly_inflation)]

        else:
            df_loaded = pd.read_csv(
                file_name,
                dtype={'Capital_contribution': float},  # Set column dtypes
                parse_dates=True  # Parse dates if present (optional)
            )
            capital_contribution = df_loaded['Capital_contribution'].copy()
            capital_contribution = pd.Series(capital_contribution).fillna(float(0))

            # Adding the contribution value for the first year
            temp = 0
            for i, s in enumerate(df_loaded['Locked'][age_of_contribution_year * 12: age_of_contribution_year * 12 + 12]):
                temp = contribution_value
                if not s:  # Se status for False
                    capital_contribution[age_of_contribution_year*12+i] = contribution_value

            # it will add the next contributions with the inflation adjustment
            aporte = 0
            for h in range(age_of_contribution_year + 1, age_of_contribution_year + contribution_length_year):
                aporte = round((aporte + temp) * (1 + yearly_inflation), 2)
                temp = 0
                for i, s in enumerate(df_loaded['Locked'][h * 12: h * 12 + 12]):
                    if not s:  # Se status for False
                        capital_contribution[h * 12 + i] = aporte

        #clear the list
        passive_income = (time_length - income_age) * [float(0)] + income_age * [0]

        # The value of first year of passive income is correct by inflation from the age of contribution to the age of retirement
        passive_income[12 * income_age_year:12 * income_age_year + 12] = 12 * [round(float(passive_income_value * (1 + yearly_inflation) ** (income_age_year - (reference_year - birth_year))), 2)]
        for j in range(income_age_year + 1, time_length_year):
            passive_income[j * 12:j * 12 + 12] = 12 * [round(passive_income[12 * j - 1] * (1 + yearly_inflation), 2)]

        last_amount = Accumulated_amount[-1]

        # clear the list
        Accumulated_amount = time_length * [float(0)]
        # the first mount is yield
        Accumulated_amount[0] = (capital_contribution[0]) * (1 + monthly_interest)

        # A new interest is taken from the new contribution, the previous accumulated amount and from the subtraction from the passive income for the next months
        for i in range(1, time_length):
            Accumulated_amount[i] = (capital_contribution[i] + Accumulated_amount[i - 1] - passive_income[i]) * ( 1 + monthly_interest)

        # Check if Accumulated_amount changes when the contribution value changes. Otherwise, it the loop will hange.
        current_amount = Accumulated_amount[-1]  # Get the latest value
        if current_amount == last_amount:
            print("There are no time slot to increase the amount of savings.")
            break

    return capital_contribution, passive_income, Accumulated_amount


def get_investing_assets(country, asset_type):
    assets_list = []
    try:
        if asset_type == 'funds':
            assets_list = investpy.funds.get_funds(country)  #https://investpy.readthedocs.io/_api/funds.html
        elif asset_type == 'stocks':
            assets_list = investpy.stocks.get_stocks(country)  #https://investpy.readthedocs.io/_api/funds.html
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

def plot_yield(capital_contribution, Accumulated_amount, passive_income, years, color, name):
    plt.plot(years, Accumulated_amount[0:1200:6], label=f'{name}: Amount of savings ', color=color)
    plt.plot(years, passive_income[0:1200:6], label=f'{name}: Passive incomes', color=color)
    plt.plot(years, capital_contribution[0:1200:6], label=f'{name}: Passive incomes', color=color)



if __name__ == '__main__':
    print_hi('PyCharm')


# print(df_loaded)  # First 5 rows
# print(df_loaded.dtypes)  # Column data types
# print(f"The load value is {df_loaded.loc[350].iloc[0]}")
# print(f"The load value is {df_loaded.loc[350].iloc[3]}")
# print(f"The load value is {df_loaded.loc[351].iloc[0]}")
# print(f"The load value is {df_loaded.loc[351].iloc[3]}")

assets_list = get_investing_assets('sweden', 'funds')
search_results = yf.Search(assets_list[190])
info = search_results.all

symbol_yf = info['quotes'][0]['symbol']
date_start = '2023-01-03'
date_end = "2025-01-03"
data = yf.download(symbol_yf, start=date_start, end=date_end)
valor_inicial = data.loc[data.index[0], 'Close'].iloc[0]
valor_final = data.loc[data.index[-1], 'Close'].iloc[0]
print(valor_inicial)
print(valor_final)

reference_date = dict(year = 2008, month = 1)

# calculate the inflation and index
IPCA = annual_mean_inflation(f"{reference_date['year']}-01-01","IPCA")
IGPM = annual_mean_inflation(f"{reference_date['year']}-01-01","IGPM")
Selic = annual_mean_inflation("2024-04-01","Selic")
itau = (1+IGPM)*(1+0.06) - 1
print(f"Mean inflation IGPM: {IGPM}")
print(f"Mean inflation IPCA: {IPCA}")
print(f"Mean inflation SELIC: {Selic}")
print(f"Mean yield IGPM+6: {itau}")

years = [i * 0.5 for i in range(0, 200)]

# IGPM + 6%
refresh = False
asset_name = "IGPM+6%"
financial_params['yearly_inflation'] = IPCA
financial_params['yearly_interest'] = itau
financial_params['reference_year'] = reference_date['year']
financial_params['age_of_contribution_year'] = 28
financial_params['contribution_length_year'] = 17
financial_params['contribution_value'] = 1
financial_params['passive_income_value'] = 3700

capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_00.csv',refresh=refresh)
plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "red")

df = pd.DataFrame(list(zip(capital_contribution, passive_income, [round(p, 2) for p in Accumulated_amount])), columns=[f"{asset_name} Capital_contribution",f"{asset_name} passive_income",f"{asset_name} Accumulated_amount"])

# # Finserve Global Security Fund I SEK R
# refresh = False
# asset_name = "Finserve Global Security Fund I SEK R"
# financial_params['yearly_inflation'] = IPCA
# financial_params['yearly_interest'] = 0.2679174
# financial_params['reference_year'] = reference_date['year']
# financial_params['age_of_contribution_year'] = 44
# financial_params['contribution_length_year'] = 1
# financial_params['contribution_value'] = 1000
# financial_params['passive_income_value'] = 1250
#
# capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_01.csv', refresh=refresh)
# plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "green")
#
# df = pd.concat([pd.Series(passive_income, name=f"{asset_name} passive_income"), df], axis=1)
# df = pd.concat([pd.Series(Accumulated_amount, name=f"{asset_name} Accumulated_amount"), df], axis=1)
# df = pd.concat([pd.Series(capital_contribution, name=f"{asset_name} capital_contribution"), df], axis=1)
#
#
# # Spiltan Globalfond Investmentbolag
# refresh = False
# asset_name = "Spiltan Globalfond Investmentbolag"
# financial_params['yearly_inflation'] = IPCA
# financial_params['yearly_interest'] = 0.2605262
# financial_params['reference_year'] = reference_date['year']
# financial_params['age_of_contribution_year'] = 44
# financial_params['contribution_length_year'] = 1
# financial_params['contribution_value'] = 1000
# financial_params['passive_income_value'] = 1250
#
# capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_02.csv', refresh=refresh)
# plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "blue")
#
# df = pd.concat([pd.Series(passive_income, name=f"{asset_name} passive_income"), df], axis=1)
# df = pd.concat([pd.Series(Accumulated_amount, name=f"{asset_name} Accumulated_amount"), df], axis=1)
# df = pd.concat([pd.Series(capital_contribution, name=f"{asset_name} capital_contribution"), df], axis=1)
#
# #Tellus Midas
# refresh = False
# asset_name = "Tellus Midas"
# financial_params['yearly_inflation'] = IPCA
# financial_params['yearly_interest'] = 0.2552236
# financial_params['reference_year'] = reference_date['year']
# financial_params['age_of_contribution_year'] = 44
# financial_params['contribution_length_year'] = 1
# financial_params['contribution_value'] = 1000
# financial_params['passive_income_value'] = 1250
#
# capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_03.csv', refresh=refresh)
# plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "yellow")
#
# df = pd.concat([pd.Series(passive_income, name=f"{asset_name} passive_income"), df], axis=1)
# df = pd.concat([pd.Series(Accumulated_amount, name=f"{asset_name} Accumulated_amount"), df], axis=1)
# df = pd.concat([pd.Series(capital_contribution, name=f"{asset_name} capital_contribution"), df], axis=1)
#
# #East Capital Balkans A1 SEK
# refresh = False
# asset_name = "East Capital Balkans A1 SEK"
# financial_params['yearly_inflation'] = IPCA
# financial_params['yearly_interest'] = 0.2967898
# financial_params['reference_year'] = reference_date['year']
# financial_params['age_of_contribution_year'] = 44
# financial_params['contribution_length_year'] = 1
# financial_params['contribution_value'] = 1000
# financial_params['passive_income_value'] = 1250
#
# capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_04.csv', refresh=refresh)
# plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "pink")
#
# df = pd.concat([pd.Series(passive_income, name=f"{asset_name} passive_income"), df], axis=1)
# df = pd.concat([pd.Series(Accumulated_amount, name=f"{asset_name} Accumulated_amount"), df], axis=1)
# df = pd.concat([pd.Series(capital_contribution, name=f"{asset_name} capital_contribution"), df], axis=1)



# It save the lists in a excell file.
df.to_csv("invest.csv", index=False)  # Remove `index=False` to keep row numbers

plt.title('Yield Projection (2024)')
plt.xlabel('Month')
plt.ylabel('Value (BRL)')
plt.legend()
plt.grid()
plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
