import investing as pi
import yfinance as yf
from datetime import datetime
from functools import wraps
import time

today = datetime.now().strftime("%Y-%m-%d")
reference_date = dict(year = 2008, month = 1)
birth_date = dict(year = 1980, month = 8, day = 10)

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    wait = (backoff_in_seconds * (2 ** x))
                    print(f"Attempt {x + 1} failed. Retrying in {wait} seconds...")
                    time.sleep(wait)
                    x += 1
        return wrapper
    return decorator


# print(df_loaded)  # First 5 rows
# print(df_loaded.dtypes)  # Column data types
# print(f"The load value is {df_loaded.loc[350].iloc[0]}")
# print(f"The load value is {df_loaded.loc[350].iloc[3]}")
# print(f"The load value is {df_loaded.loc[351].iloc[0]}")
# print(f"The load value is {df_loaded.loc[351].iloc[3]}")

country = 'sweden'
df = pi.get_investing_assets(country=country, asset_type='funds')

# Add CAGR (Compound Annual Growth Rate) to df
df['cagr'] = float(0)

for i in range(len(df)):
    date_start = '2022-06-01'
    date_end = today

    search_results = yf.Search(df.loc[i]['symbol'])
    info = search_results.all
    try:
        #shortname_yf = info['quotes'][0]['shortname']
        symbol_yf = info['quotes'][0]['symbol']
    except IndexError:
        continue

    try:
        # @retry_with_backoff(retries=10, backoff_in_seconds=4)
        # def download_with_retry(symbol, start, end):
        #     return yf.download(symbol, start=start, end=end)
        # data = download_with_retry(symbol_yf, start=date_start, end=date_end)

        data = yf.download(symbol_yf, start=date_start, end=date_end)
    except Exception as e:
        print(f"There is no data for this asset: {str(e)}")
    else:
        date_start = str(data.index[0])[0:10]
        date_end = str(data.index[-1])[0:10]

        valor_inicial = data.loc[data.index[0], 'Close'].iloc[0]
        valor_final = data.loc[data.index[-1], 'Close'].iloc[0]

        sharpe_ratio = pi.sharpe_ratio(data['Close'], risk_free_rate=0.044)
        rate=pi.compound_growth_rate(initial_value=valor_inicial, final_value=valor_final, days=len(data.index), period='y')

        df.loc[i, "cagr"] = rate
        df.loc[i, "sharpe_ratio"] = sharpe_ratio

        print(f"{i} {df.loc[i]['isin']} yearly growth rate is {rate}")
        print(f'    {date_start} = {valor_inicial}')
        print(f'    {date_end} = {valor_final}')

df.to_csv(
    f'funds_{country}.csv',  # File path/name
    index=True,             # Exclude row indices
    float_format='%.4f',    # Round floats to 2 decimal places
    encoding='utf-8'        # Set encoding (optional)
)

#df_loaded = pd.read_csv('investment_data.csv')

# sort the cagr assets descending
df_cagr = df.sort_values('cagr', ascending=False)
print(df_cagr[0:30])

# # calculate the inflation and index
# IPCA = annual_mean_inflation(f"{reference_date['year']}-01-01","IPCA")
# IGPM = annual_mean_inflation(f"{reference_date['year']}-01-01","IGPM")
# Selic = annual_mean_inflation("2024-04-01","Selic")
# itau = (1+IGPM)*(1+0.06) - 1
# print(f"Mean inflation IGPM: {IGPM}")
# print(f"Mean inflation IPCA: {IPCA}")
# print(f"Mean inflation SELIC: {Selic}")
# print(f"Mean yield IGPM+6: {itau}")
#
# years = [i * 0.5 for i in range(0, 1200)]
#
# # IGPM + 6%
# refresh = False
# asset_name = "IGPM+6%"
# financial_params['yearly_inflation'] =0.05780134434278720 #IPCA
# financial_params['yearly_interest'] = 0.13919474095572400 #itau
# financial_params['reference_year'] = reference_date['year']
# financial_params['age_of_contribution_year'] = 44
# financial_params['contribution_length_year'] = 1
# financial_params['passive_income_value'] = 4000
#
# capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_00.csv',refresh=refresh)
# plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "red")
# df = pd.DataFrame(list(zip(capital_contribution, passive_income, [round(p, 2) for p in Accumulated_amount])), columns=[f"{asset_name} Capital_contribution",f"{asset_name} passive_income",f"{asset_name} Accumulated_amount"])
#
# # Finserve Global Security Fund I SEK R
# refresh = False
# asset_name = "Finserve Global Security Fund I SEK R"
# financial_params['yearly_inflation'] = IPCA
# financial_params['yearly_interest'] = 0.2679174
# financial_params['reference_year'] = reference_date['year']
# financial_params['age_of_contribution_year'] = 44
# financial_params['contribution_length_year'] = 1
# financial_params['passive_income_value'] = 2000
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
# financial_params['passive_income_value'] = 1250
#
# capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params, file_name='asset_04.csv', refresh=refresh)
# plot_yield(capital_contribution, Accumulated_amount, passive_income, years, name=asset_name, color = "pink")
#
# df = pd.concat([pd.Series(passive_income, name=f"{asset_name} passive_income"), df], axis=1)
# df = pd.concat([pd.Series(Accumulated_amount, name=f"{asset_name} Accumulated_amount"), df], axis=1)
# df = pd.concat([pd.Series(capital_contribution, name=f"{asset_name} capital_contribution"), df], axis=1)
#
#
#
# # It save the lists in a excell file.
# df.to_csv("invest.csv", index=False)  # Remove `index=False` to keep row numbers
#
# plt.title('Yield Projection (2024)')
# plt.xlabel('Month')
# plt.ylabel('Value (BRL)')
# plt.legend()
# plt.grid()
# plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
