import sys
sys.path.append('/home/ec2-user/virenv/pcv')

from lsr import (
    account_peace77t7,
    account_peace77t6,
    account_peace77t5,
    account_peace77t4)

login_url = 'https://localhost:5000/sso/Login?forwardTo=22&RL=1&ip2loc=US'

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.BinaryLocation = "/usr/bin/chromium-browser"
options.add_argument('--allow-running-insecure-content')
options.add_argument('--allow-insecure-localhost')

user_name_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[1]/div/div[2]/div/input"
password_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[1]/div/div[3]/div/input"
login_button_x_path = "/html/body/section[1]/div/div/form/div/div[1]/div[4]/div/div/div[2]/div[1]/button"

for account in [account_peace77t7, account_peace77t6, account_peace77t5, account_peace77t4]:
    driver = webdriver.Chrome(options=options)
    driver.get(login_url)
    driver.find_element_by_xpath(user_name_x_path).send_keys(account.get('username'))
    driver.find_element_by_xpath(password_x_path).send_keys(account.get('lsr'))
    driver.find_element_by_xpath(login_button_x_path).click()
    driver.quit()

