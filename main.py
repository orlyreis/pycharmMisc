import investing as pi
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

today = datetime.now().strftime("%Y-%m-%d")
reference_date = dict(year = 2008, month = 1)
birth_date = dict(year = 1980, month = 8, day = 10)


country = 'denmark'
funds = 'funds'

#pi.get_asset_key_data(country = country,funds = funds)

df_loaded = pd.read_csv(f"funds_{country}.csv")

# sort the cagr assets descending
df_cagr = df_loaded.sort_values('cagr', ascending=False)
print(df_cagr[0:30])

# calculate the inflation and index
IPCA = pi.annual_mean_inflation(f"{reference_date['year']}-01-01","IPCA")
IGPM = pi.annual_mean_inflation(f"{reference_date['year']}-01-01","IGPM")
Selic = pi.annual_mean_inflation("2024-04-01","Selic")
itau = (1+IGPM)*(1+0.06) - 1
print(f"Mean inflation IGPM: {IGPM}")
print(f"Mean inflation IPCA: {IPCA}")
print(f"Mean inflation SELIC: {Selic}")
print(f"Mean yield IGPM+6: {itau}")

years = [i * 0.5 for i in range(0, 1200)]

portfolio = {
  "name":                     ["IGPM+6%", df_loaded.loc[32]['name'], df_loaded.loc[600]['name'], df_loaded.loc[602]['name']],
  "yearly_inflation":         [     IPCA,                      IPCA,                       IPCA,                       IPCA],
  "yearly_interest":          [     itau, df_loaded.loc[32]['cagr'], df_loaded.loc[600]['cagr'], df_loaded.loc[602]['cagr']],
  "age_of_contribution_year": [       44,                        45,                         46,                         47],
  "contribution_length_year": [        1,                        10,                          4,                          5],
  "passive_income_value":     [     4000,                      1000,                       1000,                       2000],
  "income_age_year":          [       52,                        50,                         50,                         54],
  "refresh":                  [    False,                      True,                       True,                       True]
}

#load data into a DataFrame object:
portfolio_df = pd.DataFrame(portfolio)
#print(portfolio_df)
#
for i in range(0, len(portfolio_df)):
  asset_name = portfolio_df.iloc[i, 0]
  pi.financial_params['yearly_inflation'] =portfolio_df.iloc[i, 1]
  pi.financial_params['yearly_interest'] = portfolio_df.iloc[i, 2]
  pi.financial_params['reference_year'] = reference_date['year']
  pi.financial_params['age_of_contribution_year'] = portfolio_df.iloc[i, 3]
  pi.financial_params['contribution_length_year'] = portfolio_df.iloc[i, 4]
  pi.financial_params['passive_income_value'] = portfolio_df.iloc[i, 5]
  pi.financial_params['income_age_year'] = portfolio_df.iloc[i, 6]
  refresh = portfolio_df.iloc[i, 7]
  #
  capital_contribution, accumulated_amount, passive_income, = pi.assets_projection(pi.financial_params, file_name='asset_00.csv', refresh=refresh)
  pi.plot_yield(capital_contribution, accumulated_amount, passive_income, years, name=asset_name)
  pi.generate_csv(asset_name, capital_contribution, accumulated_amount, passive_income)

plt.title('Yield Projection (2024)')
plt.xlabel('Month')
plt.ylabel('Value (BRL)')
plt.legend()
plt.grid()
plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
