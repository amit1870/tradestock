import sys
import argparse
import time
sys.path.append('/home/ec2-user/virenv/pcv')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lsr import ACCOUNTS

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
    parser.add_argument('--username', default='all', help='For peace77t7. Use only t7')
    args = parser.parse_args()

    if args.username == 'all':
        accounts = [account for key, account in ACCOUNTS.items()]
    else:
        accounts = [ACCOUNTS.get(args.username)]

    if accounts:
        print("Authentication started for {}".format(accounts))
        auto_mode_on_accounts(accounts)
        print("Authentication finished!!")
