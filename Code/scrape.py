from config import url, user_email, user_password
from splinter import Browser
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import time
import warnings
from webdriver_manager.firefox import GeckoDriverManager
warnings.simplefilter(action='ignore', category=FutureWarning)

def scrape ():
    # Browser setup
    executable_path = {'executable_path': GeckoDriverManager().install()}
    browser = Browser('firefox', **executable_path, headless=True)

    # Log In to Mint
    browser.visit(url)
    browser.find_by_id('ius-identifier').first.fill(user_email)
    browser.find_by_id('ius-sign-in-submit-btn').first.click()
    time.sleep(5)
    browser.find_by_id('ius-sign-in-mfa-password-collection-current-password').first.fill(user_password)
    browser.find_by_id('ius-sign-in-mfa-password-collection-continue-btn').first.click()
    time.sleep(10)

    # Go to transactions page
    browser.click_link_by_partial_text('Transactions')
    time.sleep(10)

    # Getting yesterday's transactions
    html=browser.html
    transactions = pd.read_html(html)[6]
    transactions = transactions[['Date','Description','Category','Amount']].droplevel(1,axis=1)
    transactions = transactions.head(5)

    # Go to budgets page
    browser.click_link_by_partial_text('Budgets')
    time.sleep(10)

    # Get HTML 
    html=browser.html
    soup=BeautifulSoup(html,"html.parser")

    income = soup.find('div',{'class': 'BudgetCardstyle__WrapperBudget-k3uxfw-1 irMFKm'})
    income_list = income.text.split('$')
    income_title = income_list[0]
    income_list = [re.sub("[^0-9]", "", s) for s in income_list]
    income_progress = income_list[2]
    income_goal = income_list[3]
    income_details = {
        'Name': income_title,
        'Budget Amount': income_progress,
        'Amount Spent': income_goal
    }

    # Find Budget Data
    budgets = soup.find_all('div',{'class':'BudgetListstyle__BudgetListSection-sc-1oeq37j-8 fzKgiV'})[1]
    budget_items =[]
    for result in budgets.find_all('div',{'class': 'BudgetCardstyle__WrapperBudget-k3uxfw-1 irMFKm'}):
        budget_list = result.text.split('$')
        budget_name = budget_list[0]
        budget_list = [re.sub("[^0-9]", "", s) for s in budget_list]
        budget_spent = budget_list[-1]
        budget_amount = budget_list[-2]
        budget_details = {
            'Name': budget_name,
            'Budget Amount': budget_amount,
            'Amount Spent': budget_spent
        }
        budget_items.append(budget_details)

    # #Find Everything Else Data
    everything_else = soup.find_all('div',{'class': 'EverythingElsestyle__EverythingElseListSection-n6fqz4-0 fAfoAa'})[1]
    everything_list = everything_else.text.split('$')
    everything_title = everything_list[0]
    everything_list = [re.sub("[^0-9]", "", s) for s in everything_list]
    everything_progress = income_list[2]
    everything_goal = income_list[3]
    everything_details = {
        'Name': everything_title,
        'Budget Amount': everything_progress,
        'Amount Spent': everything_goal
    }

    # Close browser
    browser.quit()

    # Converting dictonaries to dataframes
    income_df = pd.DataFrame([income_details])
    budget_df = pd.DataFrame(budget_items)
    everything_df = pd.DataFrame([everything_details])

    # Combining all data frames
    all_budgets = pd.concat([income_df,budget_df,everything_df], ignore_index=True)
    all_budgets[all_budgets.columns[1:]] = all_budgets[all_budgets.columns[1:]].astype(int)
    all_budgets['Remaining Budget'] = all_budgets['Budget Amount'] - all_budgets['Amount Spent']
    all_budgets
    
    #return functions
    return all_budgets, transactions

