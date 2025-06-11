# This is a sample Python script.
import numpy as np
import yfinance as yf
import investpy
import pandas as pd
from bcb import sgs
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import matplotlib.pyplot as plt

today = datetime.now().strftime("%Y-%m-%d")

financial_params = dict(yearly_interest=0.13499942436095425, yearly_inflation=0.059171235294, time_length_year=100,
                        contribution_length_year=20, income_age_year=50, passive_income_value=8000,
                        reference_year=2008, reference_month=1, birth_year=1980, birth_month=8)



def assets_projection(financial_params, file_name, refresh=False):
    yearly_interest = financial_params['yearly_interest']
    yearly_inflation = financial_params['yearly_inflation']
    time_length_year = financial_params['time_length_year']
    contribution_length_year = financial_params['contribution_length_year']
    income_age_year = financial_params['income_age_year']
    initial_contribution = 100000
    passive_income_value = financial_params['passive_income_value']
    reference_year = financial_params['reference_year']
    birth_year = financial_params['birth_year']
    birth_month = financial_params['birth_month']

    age_of_contribution = (int(today[0:4]) - birth_year)*12 + int(today[5:7]) - birth_month
    contribution_length = contribution_length_year * 12
    income_age = income_age_year*12
    monthly_interest = (1 + yearly_interest) ** (1 / 12) - 1
    time_length = time_length_year * 12
    Accumulated_amount: list[float] = time_length * [float(0)]
    flag = 1
    limit = 10
    limit_superior = initial_contribution
    limit_inferior = 0
    while abs(Accumulated_amount[-1]) > limit or flag == 1:
        flag = 0
        #clear the list
        if refresh:
            capital_contribution = age_of_contribution * [float(0)] + contribution_length * [float(0)] + (
                    time_length - contribution_length - age_of_contribution) * [float(0)]

            contribution_value = initial_contribution
            # it will add the next contributions with the inflation adjustment
            for i in range(age_of_contribution, age_of_contribution + contribution_length):
                if float(i/12).is_integer():
                    contribution_value = round(contribution_value * (1 + yearly_inflation), 10)

                capital_contribution[i] = contribution_value

        else:
            df_loaded = pd.read_csv(
                file_name,
                dtype={'Capital_contribution': float},  # Set column dtypes
                parse_dates=True  # Parse dates if present (optional)
            )
            capital_contribution = df_loaded['Capital_contribution'].copy()
            capital_contribution = pd.Series(capital_contribution).fillna(float(0))

            contribution_value = initial_contribution
            # Adding the contribution value for the first year
            for i in range(age_of_contribution, age_of_contribution + contribution_length):
                if float(i/12).is_integer():
                    contribution_value = round(contribution_value * (1 + yearly_inflation), 2)

                if not df_loaded['Locked'][i]:  # Se status for False
                    capital_contribution[i] = contribution_value

        #clear the list
        passive_income = (time_length - income_age) * [float(0)] + income_age * [0]

        passive_value = round(float(passive_income_value * (1 + yearly_inflation) ** (income_age_year - (reference_year - birth_year))),2)
        for i in range(income_age, time_length_year*12):
            if float(i/12).is_integer():
                passive_value = round(passive_value * (1 + yearly_inflation), 10)

            passive_income[i] = passive_value

        last_amount = Accumulated_amount[-1]

        # clear the list
        Accumulated_amount = time_length * [float(0)]
        # the first mount is yield
        Accumulated_amount[0] = (capital_contribution[0]) * (1 + monthly_interest)

        # A new interest is taken from the new contribution, the previous accumulated amount and from the subtraction from the passive income for the next months
        for i in range(0, time_length):
            Accumulated_amount[i] = (capital_contribution[i] + Accumulated_amount[i - 1] - passive_income[i]) * ( 1 + monthly_interest)

        if Accumulated_amount[-1] > limit:
            limit_superior = initial_contribution
        elif Accumulated_amount[-1] < -limit:
            limit_inferior = initial_contribution

        initial_contribution = (limit_superior + limit_inferior)/2

        # Check if Accumulated_amount changes when the contribution value changes. Otherwise, it the loop will hange.
        current_amount = Accumulated_amount[-1]  # Get the latest value
        if current_amount == last_amount:
            print("There are no time slot to increase the amount of savings.")
            break

    return pd.Series(capital_contribution), pd.Series(Accumulated_amount), pd.Series(passive_income)


def get_investing_assets(country, asset_type):
    #assets_list = []
    try:
        if asset_type == 'funds':
            df = investpy.funds.get_funds(country)  #https://investpy.readthedocs.io/_api/funds.html
        elif asset_type == 'stocks':
            df = investpy.stocks.get_stocks(country)  #https://investpy.readthedocs.io/_api/funds.html
    except:
        print(f'Wrong country: {country}')
        return None
    else:
        # Chamar a função para ler o arquivo
        #print(f'Fetching {asset_type} list from {country}')
        #symbol_list = list(df['symbol'])
        return df


def annual_mean_inflation(start_year, code):
    #Indicador	Código BCB
    #IPCA	433
    #IGPM (FGV)	189
    #Selic	11
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

def plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name):
    plt.plot(years, Accumulated_amount, label=f'{name}: Amount of savings ')
    #plt.plot(years, passive_income, label=f'{name}: Passive incomes')
    #plt.plot(years, capital_contribution, label=f'{name}: Passive incomes')

#Compound Growth Rate
def compound_growth_rate(initial_value, final_value, days, period='y'):
    cgr = (final_value/initial_value)**(1/days)-1
    if period == 'd':
        return cgr
    elif period == 'm':
        return (1+cgr)**21-1
    elif period == 'y':
        return (1+cgr)**252-1

def sharpe_ratio_calculator(data, risk_free_rate=0.02):
    # Passo 2: Calculate daily returns
    daily_return = data.pct_change().dropna()

    # Passo 4: Calcular métricas
    avg_daily_return = daily_return.mean()
    std_daily_return = daily_return.std()

    # Annualização
    yearly_return = float(avg_daily_return.iloc[0]) * 252
    yearly_volatility = float(std_daily_return.iloc[0]) * np.sqrt(252)

    # Sharpe Ratio
    sharpe_ratio = (yearly_return - risk_free_rate) / yearly_volatility

    print(f"Retorno anualizado: {yearly_return:.2%}")
    print(f"Volatilidade anualizada: {yearly_volatility:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    return sharpe_ratio


def safe_download(ticker, start, end):
    try:
        #session = Session()
        retry = Retry(total=10, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        #session.mount('http://', adapter)
        #session.mount('https://', adapter)

        data = yf.download(
            ticker,
            start=start,
            end=end,
            timeout=30,
            #session=session
        )
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_asset_key_data(country = 'luxembourg', funds = 'funds'):

    df = get_investing_assets(country=country, asset_type=funds)

    for i in range(len(df)):
        date_start = '2022-07-01'
        date_end = today

        search_results = yf.Search(df.loc[i]['symbol'])
        info = search_results.all
        try:
            #shortname_yf = info['quotes'][0]['shortname']
            symbol_yf = info['quotes'][0]['symbol']
        except IndexError:
            continue

        try:
            data = safe_download(symbol_yf, start=date_start, end=date_end)
        except Exception as e:
            print(f"There is no data for this asset: {str(e)}")
        else:
            date_start = str(data.index[0])[0:10]
            date_end = str(data.index[-1])[0:10]

            initial_value = data.loc[data.index[0], 'Close'].iloc[0]
            final_value = data.loc[data.index[-1], 'Close'].iloc[0]

            rate=compound_growth_rate(initial_value=initial_value, final_value=final_value, days=len(data.index), period='y')

            print(f"{i} {df.loc[i]['isin']} yearly growth rate is {rate}")
            print(f'    {date_start} = {initial_value}')
            print(f'    {date_end} = {final_value}')

            sharpe_ratio = sharpe_ratio_calculator(data['Close'], risk_free_rate=0.044)
            df.loc[i, "cagr"] = rate
            df.loc[i, "sharpe_ratio"] = sharpe_ratio


    df.to_csv(
        f'funds_{country}.csv',  # File path/name
        index=True,             # Exclude row indices
        float_format='%.4f',    # Round floats to 2 decimal places
        encoding='utf-8'        # Set encoding (optional)
    )


def generate_csv(asset_name, capital_contribution, accumulated_amount, passive_income):
    #it creates the csv file with contribution, accumulated amount and passive income
    # Criar MultiIndex para colunas
    colunas = pd.MultiIndex.from_tuples([
        (f'{asset_name}', 'Contribution'),
        (f'{asset_name}', 'Accumulated Amount'),
        (f'{asset_name}', 'Passive Income')
    ])

    df = pd.DataFrame({
        (f'{asset_name}', 'Contribution'): capital_contribution.round(2),
        (f'{asset_name}', 'Accumulated Amount'): accumulated_amount.round(2),
        (f'{asset_name}', 'Passive Income'): passive_income.round(2)
    })

    # Reorganiza as colunas na ordem definida pelo MultiIndex (opcional)
    df = df[colunas]
    df.columns.names = ['Asset', '']

    df.to_csv(f"whale_{asset_name}.csv", index=True)  # Remove `index=False` to keep row numbers
    print(df)

