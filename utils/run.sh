#!/bin/bash
echo "Running....."

BASE_DIR="/home/ec2-user/virenv"
CODE_DIR="$BASE_DIR/pcv"
SERVER_DIR="$BASE_DIR/pcv/clientportal"
LOG_FILE="/home/ec2-user/virenv/stocks.log"
OTHER_LOG_FILE="/home/ec2-user/virenv/other.log"
NEW_LOG_FILE="/home/ec2-user/virenv/stocks.log.1"
TOKEN_FILE_PATH="/home/ec2-user/virenv/token.json"

LOG_SIZE=500000 # 5MB
SLEEP_SECONDS=1200 # Seconds
NAP_SECONDS=120 # Seconds
EMAIL_SCHEDULE="H"
STOCK_TYPE=0
NEW_LINE=$'\n'

declare -a usernames=("peace77t7" "peace77t6" "peace77t5" "peace77t4")
declare -a accounts=("U5931342" "U6092014" "U6050929" "U6498436")
declare -a passwords=( "$@" )

# Activate vitural env and export PYTHONPATH
cd ${BASE_DIR} || exit
source bin/activate
export PYTHONPATH="${CODE_DIR}"
export DISPLAY="localhost:1"
alias python='$BASE_DIR/bin/python'

# Run server
java_server_id=$(pidof java)
if [[ -z $java_server_id ]]; then
    cd ${SERVER_DIR} || exit
    bash "${SERVER_DIR}/bin/run.sh" root/conf.yaml &
fi

# Remove $LOG_FILE if already found.
if [ -f "$LOG_FILE" ]; then
    rm -f ${LOG_FILE} ${OTHER_LOG_FILE}
fi

# Add new  $LOG_FILE
touch ${LOG_FILE} ${OTHER_LOG_FILE}

# Remove $NEW_LOG_FILE if already found.
if [ -f "$NEW_LOG_FILE" ]; then
    rm -f ${NEW_LOG_FILE}
fi

# Check if email program is already running
email_py_program_id=$(pgrep -f "[p]ython $CODE_DIR/utils/send_email.py")
if [[ -z $email_py_program_id ]]; then
    # Run Email send command
    python "${CODE_DIR}/utils/send_email.py" --token=${TOKEN_FILE_PATH} --schedule=${EMAIL_SCHEDULE} &
fi

while true; do

    # Check log file size and mv $LOG_FILE when size is $LOG_SIZE
    CURRENT_LOG_SIZE=$(stat -c%s $LOG_FILE)
    if (( CURRENT_LOG_SIZE > LOG_SIZE )); then
        mv $LOG_FILE $NEW_LOG_FILE
        touch $LOG_FILE
    fi

    for (( i = 0; i < ${#usernames[@]}; i++ )); do
        RUNNING_DATE=$(date)
        echo "[${usernames[i]}  :: ${accounts[i]} :: $RUNNING_DATE]" >> $LOG_FILE
        python "${CODE_DIR}/ibkrs/all_stocks.py" --username "${usernames[i]}" --passkey "${passwords[i]}"  \
               --account-id "${accounts[i]}" --stock-type "${STOCK_TYPE}" >> ${LOG_FILE} 2>&1
        echo "$NEW_LINE" >> ${LOG_FILE}

        echo "Going to nap for ${NAP_SECONDS}sec.."
        sleep ${NAP_SECONDS}
    done

    echo "Going to sleep for ${SLEEP_SECONDS}sec..."
    sleep ${SLEEP_SECONDS}

done

echo "Finished!!"