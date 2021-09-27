import os
import argparse
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from utils.settings import ACCOUNTS
from utils.lsr_opr import get_context, decrypt_lsr

def _auto_mode_on_accounts(accounts, url=None, sleep_sec=5):

    # export DISPLAY to localhost:1 for web driver
    os.environ["DISPLAY"] = "localhost:1"

    if url is None:
        LOGIN_URL = 'https://localhost:5000/sso/Login?forwardTo=22&RL=1&ip2loc=US'
    else:
        LOGIN_URL = url

    options = Options()
    options.BinaryLocation = "/usr/bin/chromium-browser"
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--allow-insecure-localhost')

    user_name_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[1]/div/div[2]/div/input"
    password_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[1]/div/div[3]/div/input"
    login_button_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[4]/div/div/div[2]/div[1]/button"

    authenticated_accounts = []
    for account in accounts:
        try:    
            driver = webdriver.Chrome(options=options)
            driver.get(LOGIN_URL)
            driver.find_element_by_xpath(user_name_x_path).send_keys(account.get('username'))
            driver.find_element_by_xpath(password_x_path).send_keys(account.get('lsr'))
            driver.find_element_by_xpath(login_button_x_path).click()
            authenticated_accounts.append(account)
            time.sleep(sleep_sec)
            driver.quit()
        except WebDriverException as e:
            pass

    return authenticated_accounts

def _update_accounts(usernames, passwords):
    context = get_context()
    authenticated_accounts = []

    for idx,username in enumerate(usernames):    
        accounts = [account for key, account in ACCOUNTS.items()]

        for account in accounts:
            account_lsr = account.get('lsr')
            passkey = passwords[idx]
            if account.get('username') == username and decrypt_lsr(context, passkey, account_lsr):
                    account['lsr'] = passkey
                    authenticated_accounts.append(account)
                    break
            elif account.get('username') == username and not decrypt_lsr(context, passkey, account_lsr):
                break

    return authenticated_accounts

def auto_mode_on_accounts(usernames, passwords):
    updated_accounts = _update_accounts(usernames, passwords)
    authenticated_accounts = _auto_mode_on_accounts(updated_accounts)
    return authenticated_accounts

      
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Authenticate Interactive Brokers.')
    parser.add_argument('--usernames', required=True, help='Accounts common seperated.')
    parser.add_argument('--passwords', required=True, help='Passwords common seperated.')
    args = parser.parse_args()
    if args.usernames and args.passwords:
        print("Authentication started for {} accounts...".format(args.username))
        successfully_authenticated_accounts = auto_mode_on_accounts(args.usernames, args.passwords)
        print("Authentication successful for {} accounts!!".format(successfully_authenticated_accounts))
