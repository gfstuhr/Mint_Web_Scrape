from config import url, user_email, user_password
from splinter import Browser
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def scrape ():
    # Browser setup
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

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

    # Defining yesterday's date
    yesterday=datetime.now()-timedelta(1)
    yesterday=datetime.strftime(yesterday, '%b %#d')

    # Getting yesterday's transactions
    html=browser.html
    transactions = pd.read_html(html)[6]
    transactions = transactions[['Date','Description','Category','Amount']].droplevel(1,axis=1)
    transactions=transactions[transactions['Date']==yesterday]

    # Go to budgets page
    browser.click_link_by_partial_text('Budgets')
    time.sleep(10)

    # Get HTML 
    html=browser.html
    soup=BeautifulSoup(html,"html.parser")

    # Find Income Data
    income = soup.find('ul',id='incomeBudget-list-body').find_all('strong')
    income_title = income[0].text
    income_progress = income[1].text
    income_goal = income[2].text
    income_details = {
        'Name': income_title,
        'Budget Amount': income_progress,
        'Amount Spent': income_goal
    }

    # Find Budget Data
    budgets = soup.find('ul', id='spendingBudget-list-body')
    budget_list =[]
    for result in budgets.find_all('li',id=re.compile('budget-')):
        budget_items = result.find_all('strong')
        budget_name = budget_items[0].text
        budget_spent = budget_items[1].text
        budget_amount = budget_items[2].text
        budget_details = {
            'Name': budget_name,
            'Budget Amount': budget_amount,
            'Amount Spent': budget_spent
        }
        budget_list.append(budget_details)

    #Find Everything Else Data
    everything_else = soup.find('li',id='spendingEE-list-total').find_all('strong')
    everything_title = everything_else[0].text
    everything_spent = everything_else[1].text
    everything_goal = everything_else[2].text
    everything_details = {
        'Name': everything_title,
        'Budget Amount': everything_spent,
        'Amount Spent': everything_goal
    }

    # Close browser
    browser.quit()

    # Converting dictonaries to dataframes
    income_df = pd.DataFrame([income_details])
    budget_df = pd.DataFrame(budget_list)
    everything_df = pd.DataFrame([everything_details])

    # Combining all data frames
    all_budgets = pd.concat([income_df,budget_df,everything_df], ignore_index=True)
    all_budgets[all_budgets.columns[1:]] = all_budgets[all_budgets.columns[1:]].replace('[\$,]', '', regex=True).astype(int)
    all_budgets['Remaining Budget'] = all_budgets['Budget Amount'] - all_budgets['Amount Spent']

    #return functions
    return all_budgets, transactions

