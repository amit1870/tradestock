
# Start VNC server to DISPLAY UI activity
sudo systemctl status vncserver@:1
sudo systemctl start vncserver@:1

# Install java, virtual env package
sudo apt install openjdk-11-jdk python3-pip python3-venv net-tools

# Install google chrome and chrome driver after checking google-chrome version
URL: https://chromedriver.chromium.org/downloads
google-chrome --version
wget https://chromedriver.storage.googleapis.com/95.0.4638.17/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver

# Create virtual env and activate it
python3 -m venv virenv
BASE_DIR="$HOME/virenv"
cd $BASE_DIR || exit
source bin/activate
CODE_DIR="$BASE_DIR/pcv"
cd $CODE_DIR || exit

# Install pip packages from requirements.txt
pip install -r requirements.txt

# Download latest Client Portal API
BASE_DIR="$HOME/virenv"
SERVER_DIR="$BASE_DIR/pcv/clientportal"
OPR="$HOME/opr"
mkdir -p ${OPR}
cd ${OPR}
wget https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip
unzip clientportal.beta.gw.zip -d ${SERVER_DIR}
cd
rm -rf ${OPR}


# Run IBKR gateway if not running
java_server_id=$(pidof java)
echo $java_server_id
BASE_DIR="$HOME/virenv"
SERVER_DIR="$BASE_DIR/pcv/clientportal"
cd ${SERVER_DIR} || exit
nohup ./bin/run.sh root/conf.yaml &
sleep 2
java_server_id=$(pidof java)
echo $java_server_id

# Run Chrome Browser
export DISPLAY="localhost:1"
chromium-browser &

# Git pull latest code base
BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
cd $CODE_DIR || exit
git restore .
git pull

# Excecute before running Python script
BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
cd ${BASE_DIR} || exit
source bin/activate
export PYTHONPATH="${CODE_DIR}"
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