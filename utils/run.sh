#!/bin/bash
echo "Running....."

BASE_DIR="/home/ec2-user/virenv"
CODE_DIR="$BASE_DIR/pcv"
LOG_FILE="/home/ec2-user/virenv/stocks.log"
NEW_LOG_FILE="/home/ec2-user/virenv/stocks.log.1"
NEW_LINE=$'\n'
LOG_SIZE=500000 # 5MB
declare -a usernames=("peace77t7" "peace77t6" "peace77t5" "peace77t4")
declare -a accounts=("U5931342" "U6092014" "U6050929" "U6498436")

# Activate vitural env and export PYTHONPATH
cd $BASE_DIR || exit
source bin/activate
export PYTHONPATH="$CODE_DIR"

# Remove $NEW_LOG_FILE if already found.
if [ -f "$NEW_LOG_FILE" ]; then
    rm -f "$NEW_LOG_FILE"
fi

while true; do

    # Check log file size and mv $LOG_FILE when size is $LOG_SIZE
    if [ -f "$LOG_FILE" ]; then
        CURRENT_LOG_SIZE=$(stat -c%s $LOG_FILE)
        if (( CURRENT_LOG_SIZE > LOG_SIZE )); then
            mv $LOG_FILE $NEW_LOG_FILE
            touch $LOG_FILE
        fi
    else
        touch $LOG_FILE
    fi

    for (( i = 0; i < ${#usernames[@]}; i++ )); do
        RUNNING_DATE=$(date)
        python "$CODE_DIR/utils/auto_mode.py --username ${usernames[i]}"  >> $LOG_FILE
        echo "${usernames[i]} :: ${accounts[i]} :: $RUNNING_DATE :: PROFIT/LOSS" >> $LOG_FILE
        python "$CODE_DIR/ibkrs/all_stocks.py" --username ${usernames[i]} --account-id ${accounts[i]} --stock-type=1 >> $LOG_FILE 2>&1
        python "$CODE_DIR/ibkrs/all_stocks.py" --username ${usernames[i]} --account-id ${accounts[i]} --stock-type=-1 >> $LOG_FILE 2>&1
        echo "$NEW_LINE" >> $LOG_FILE

        sleep 120

    done

    sleep 600

done

echo "Finished!!"