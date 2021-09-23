#!/bin/bash
echo "Running....."

BASE_DIR="/home/ec2-user/virenv"
CODE_DIR="$BASE_DIR/pcv"
LOG_FILE="/home/ec2-user/virenv/stocks.log"
NEW_LOG_FILE="/home/ec2-user/virenv/stocks.log.1"
NEW_LINE=$'\n'
LOG_SIZE=500000 # 5MB

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

    RUNNING_DATE=$(date)

    echo "peace77t7 :: U5931342 :: $RUNNING_DATE :: PROFIT" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t7 --account-id U5931342 --stock-type=1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t6 :: U6092014 :: $RUNNING_DATE :: PROFIT" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t6 --account-id U6092014 --stock-type=1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t5 :: U6050929 :: $RUNNING_DATE :: PROFIT" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t5 --account-id U6050929 --stock-type=1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t4 :: U6498436 :: $RUNNING_DATE :: PROFIT" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t4 --account-id U6498436 --stock-type=1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t7 :: U5931342 :: $RUNNING_DATE :: LOSS" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t7 --account-id U5931342 --stock-type=-1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t6 :: U6092014 :: $RUNNING_DATE :: LOSS" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t6 --account-id U6092014 --stock-type=-1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t5 :: U6050929 :: $RUNNING_DATE :: LOSS" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t5 --account-id U6050929 --stock-type=-1 >> $LOG_FILE 2>&1
    echo "$NEW_LINE" >> $LOG_FILE

    echo "peace77t4 :: U6498436 :: $RUNNING_DATE :: LOSS" >> $LOG_FILE
    python "$CODE_DIR/ibkrs/all_stocks.py" --username peace77t4 --account-id U6498436 --stock-type=-1 >> $LOG_FILE 2>&1

    sleep 600

done

echo "Finished!!"