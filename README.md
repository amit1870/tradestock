# Download Client Portal
wget https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip
You need to unzip the folder and place it in the code repo where this code is stored.

# Run server from Client Portal
$ cd clientportal
$ ./bin/run.sh root/conf.yaml &

# Authenticate opening Browser Google Chrome
URL :: https://localhost:5000/sso/Login?forwardTo=22&RL=1&ip2loc=US
Put Username and Password and authenticate to get message "Client login succeeds"

# Run `write_config.py` script to create config and update values
$ cd pcv; python3 utils/write_config.py

# Run Scripts
$ cd pcv; python3 ibkrs/all_stocks.py  --stock-type=0
