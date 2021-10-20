# Start VNC server on EC2 if not running
sudo systemctl status vncserver@:1
sudo systemctl start vncserver@:1

# Check if IBKR gateway is running
java_server_id=$(pidof java)
echo $java_server_id

# Run Server if not running
BASE_DIR="/home/ec2-user/virenv"
SERVER_DIR="$BASE_DIR/pcv/clientportal"
cd ${SERVER_DIR} || exit
./bin/run.sh root/conf.yaml &
java_server_id=$(pidof java)
echo $java_server_id

# Run Chrome Browser
export DISPLAY="localhost:1"
chromium-browser &

# Git pull latest code base
username=amit1870
passkey=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
echo "$username with password $passkey"
BASE_DIR="/home/ec2-user/virenv"
CODE_DIR="$BASE_DIR/pcv"
cd $CODE_DIR || exit
git restore .
git pull

# Excecute before running Python script
BASE_DIR="/home/ec2-user/virenv"
CODE_DIR="$BASE_DIR/pcv"
cd ${BASE_DIR} || exit
source bin/activate
export PYTHONPATH="${CODE_DIR}"
export CONFIG=Prod
alias python='$BASE_DIR/bin/python'
cd $CODE_DIR || exit

# Run any script with --passkey option first for each account
# When running next time for same account, you can skip --passkey
python3 ibkrs/all_stocks.py --username XXXXXX --account-id XXXXXX --passkey XXXXXX
python3 ibkrs/all_stocks.py --username XXXXXX --account-id XXXXXX

# Run Bollinger Band script with below command
python3 ibkrs/order_stocks_BB.py --username XXXXXX --account-id XXXXXX --passkey XXXXXX --conid 265598 --time-period 93d --period 12 --bar 1d --upper 2 --lower 2
python3 ibkrs/order_stocks_BB.py --username XXXXXX --account-id XXXXXX --conid 265598

# Run Bollinger Script with nohup command redirecting log to a file
nohup python3 ibkrs/order_stocks_BB.py --username XXXXXX --account-id XXXXXX --passkey XXXXXX --conid 265598 --time-period 93d --period 12 --bar 1d --upper 2 --lower 2  >> /home/ec2-user/virenv/figure.log &