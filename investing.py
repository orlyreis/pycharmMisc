# This is a sample Python script.
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import remove_ticks_and_titles
import pandas as pd


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

financial_params = dict(yearly_interest=0.15, yearly_inflation=0.06, time_length_year=100, age_of_contribution_year=28,
                        contribution_length_year=20, income_age_year=50, passive_income_value=4000,
                        contribution_value=100, reference_year = 2008, reference_month = 8, birth_year = 1980, birth_month = 8)

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def assets_projection(financial_params):
    yearly_interest = financial_params['yearly_interest']
    yearly_inflation = financial_params['yearly_inflation']
    time_length_year = financial_params['time_length_year']
    age_of_contribution_year = financial_params['age_of_contribution_year']
    contribution_length_year = financial_params['contribution_length_year']
    income_age_year= financial_params['income_age_year']
    contribution_value = financial_params['contribution_value']
    passive_income_value = financial_params['passive_income_value']
    reference_year = financial_params['reference_year']
    birth_year = financial_params['birth_year']

    age_of_contribution = age_of_contribution_year * 12
    contribution_length = contribution_length_year * 12
    income_age = income_age_year * 12
    monthly_interest = (1+yearly_interest)**(1/12)-1
    time_length = time_length_year * 12
    Accumulated_amount: list[float] = time_length * [float(0)]

    while Accumulated_amount[-1] < 1:

        contribution_value = contribution_value + 1

        #clear the list
        capital_contribution = age_of_contribution * [float(0)] + contribution_length * [float(0)] + (time_length - contribution_length - age_of_contribution) * [float(0)]

        # Adding the contribution value for the first year
        capital_contribution[age_of_contribution_year*12: age_of_contribution_year*12+12] = 12 * [contribution_value]

        # it will add the next contributions with the inflation adjustment
        for i in range(age_of_contribution_year+1, age_of_contribution_year + contribution_length_year):
            capital_contribution[i*12:i*12+12] = 12*[round(capital_contribution[12*i-1]*(1+yearly_inflation),2)]

        #clear the list
        passive_income = (time_length - income_age) * [float(0)] + income_age * [0]

        # The value of first year of passive income is correct by inflation from the age of contribution to the age of retirement
        passive_income[12 * income_age_year:12 * income_age_year + 12] = 12 * [round(float(passive_income_value * (1 + yearly_inflation) ** (income_age_year - (reference_year-birth_year))),2)]
        for j in range(income_age_year + 1, time_length_year):
            passive_income[j*12:j*12+12] = 12*[round(passive_income[12*j-1]*(1+yearly_inflation),2)]

        # clear the list
        Accumulated_amount = time_length* [float(0)]
        # the first mount is yield
        Accumulated_amount[0] = (capital_contribution[0])*(1+monthly_interest)

        # A new interest is taken from the new contribution, the previous accumulated amount and from the subtraction from the passive income for the next months
        for i in range(1,time_length):
            Accumulated_amount[i] = (capital_contribution[i]+Accumulated_amount[i-1]-passive_income[i])*(1+monthly_interest)

    return capital_contribution, passive_income, Accumulated_amount
# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    print_hi('PyCharm')


reference_date = dict(year = 2008, month = 8)

years = [i * 0.5 for i in range(0, 200)]

capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params)
plt.plot(years, Accumulated_amount[0:1200:6], label='Amount of saving #1', color='blue')
plt.plot(years, passive_income[0:1200:6], label='Passive incomes #1', color='red')

financial_params['yearly_interest'] = 0.11
financial_params['income_age_year'] = 65
financial_params['age_of_contribution_year'] = 44
financial_params['contribution_length_year'] = 4

# It save the lists in a excell file.
df = pd.DataFrame(list(zip(capital_contribution, passive_income, [round(p, 2) for p in Accumulated_amount])), columns=["Capital_contribution","passive_income","Accumulated_amount"])
df.to_excel("invest.xlsx", index=False)  # Remove `index=False` to keep row numbers

capital_contribution, passive_income, Accumulated_amount = assets_projection(financial_params)
plt.plot(years, Accumulated_amount[0:1200:6], label='Amount of saving #2', color='green')
plt.plot(years, passive_income[0:1200:6], label='Passive incomes #2', color='black')

plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
