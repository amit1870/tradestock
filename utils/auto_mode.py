import sys
import argparse
import time
sys.path.append('/home/ec2-user/virenv/pcv')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lsr import ACCOUNTS
from get_lsr import get_context, decrypt_lsr

def auto_mode_on_accounts(accounts):
    LOGIN_URL = 'https://localhost:5000/sso/Login?forwardTo=22&RL=1&ip2loc=US'

    options = Options()
    options.BinaryLocation = "/usr/bin/chromium-browser"
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--allow-insecure-localhost')

    user_name_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[1]/div/div[2]/div/input"
    password_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[1]/div/div[3]/div/input"
    login_button_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[4]/div/div/div[2]/div[1]/button"

    for account in accounts:
        driver = webdriver.Chrome(options=options)
        driver.get(LOGIN_URL)
        driver.find_element_by_xpath(user_name_x_path).send_keys(account.get('username'))
        driver.find_element_by_xpath(password_x_path).send_keys(account.get('lsr'))
        driver.find_element_by_xpath(login_button_x_path).click()
        time.sleep(5)
        driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Authenticate Interactive Brokers.')
    parser.add_argument('--username', default='all', help='Account Number')
    parser.add_argument('--password', help='Password for accounts like account:password. If all, then enter password comma seperated.')
    args = parser.parse_args()
    
    context = get_context()

    if args.username == 'all':
        passwords = args.password.split(',')    
        accounts = [account for key, account in ACCOUNTS.items()]
        for account in accounts:
            account_lsr = account.get('lsr')
            for password in passwords:
                name, passkey = password.split(":")
                if account.get('username') == name and decrypt_lsr(context, passkey, account_lsr):
                    account['lsr'] = passkey

    else:
        accounts = [ACCOUNTS.get(args.username)]
        account = accounts[0]
        account_lsr = account.get('lsr')
        passkey = args.password
        if decrypt_lsr(context, passkey, account_lsr):
            account['lsr'] = passkey


    if accounts:
        print("Authentication started : {}".format(accounts.get('username')))
        auto_mode_on_accounts(accounts)
        print("Authentication finished!!")
