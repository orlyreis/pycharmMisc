# This is a sample Python script.
from http.cookiejar import month
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import remove_ticks_and_titles


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

yearly_inflation = 0.06
monthly_inflation = (1+yearly_inflation)**(1/12)-1
yearly_interest = 0.14
monthly_interest = (1+yearly_interest)**(1/12)-1

time_length_year = 100
time_length = time_length_year * 12

Accumulated_amount: list[float] = time_length * [float(0)]

age_of_contribution_year = 28
contribution_length_year = 20
age_of_contribution = age_of_contribution_year * 12
contribution_length = contribution_length_year * 12
retirement_age_year = 50
retirement_age = retirement_age_year * 12
passive_income_value = 8000

contribution_value = 2048

while Accumulated_amount[-1] < 1:

    contribution_value = contribution_value + 1

    #clear the list
    capital_contribution = age_of_contribution * [float(0)] + contribution_length * [float(0)] + (time_length - contribution_length - age_of_contribution) * [float(0)]

    # Adding the contribution value for the first year
    capital_contribution[age_of_contribution_year*12: age_of_contribution_year*12+12] = 12 * [contribution_value]

    # it will add the next contributions with the inflation adjustment
    for i in range(age_of_contribution_year+1, age_of_contribution_year + contribution_length_year):
        capital_contribution[i*12:i*12+12] = 12*[capital_contribution[12*i-1]*(1+yearly_inflation)]

    #clear the list
    passive_income = (time_length-retirement_age)*[float(0)]+retirement_age*[0]

    # The value of first year of passive income is correct by inflation from the age of contribution to the age of retirement
    passive_income[12*retirement_age_year:12*retirement_age_year+12] = 12*[float(passive_income_value * (1 + yearly_inflation) ** (retirement_age_year - age_of_contribution_year))]
    for j in range(retirement_age_year+1, time_length_year):
        passive_income[j*12:j*12+12] = 12*[passive_income[12*j-1]*(1+yearly_inflation)]

    # clear the list
    Accumulated_amount = time_length* [float(0)]
    # the first mount is accummulation
    Accumulated_amount[0] = (capital_contribution[0])*(1+monthly_interest)

    # A new interest is taken from the new contribution, the previous accumulated amount and from the substration from the passive income for the next months
    for i in range(1,time_length):
        Accumulated_amount[i] = (capital_contribution[i]+Accumulated_amount[i-1]-passive_income[i])*(1+monthly_interest)

print(f"contribution")
print(capital_contribution)

print(f"passive_income")
print(passive_income)

print(f"Accumulated_amount")
print(Accumulated_amount)

years = [i * 0.5 for i in range(0, 200)]
plt.plot(years, Accumulated_amount[0:1200:6], label='Amount of saving', color='blue')
plt.plot(years, passive_income[0:1200:6], label='Passive incomes', color='red')
plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
