#!/bin/bash
echo "Running....."

BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
RESOURCE_DIR="$CODE_DIR/resources"
LOG_FILE="$RESOURCE_DIR/stocks.log"
BOLLINGER_LOG_FILE="$RESOURCE_DIR/bbstock.log"
NAP_SECONDS=10 # Seconds
ALL_STOCK=0
NEW_LINE=$'\n'

declare -a usernames=("peace77t7" "peace77t6" "peace77t4" "peace77t3")
declare -a accounts=("U5931342" "U6092014" "U6498436" "U7242803")
declare -a passwords=( "$@" )

# Activate vitural env and export PYTHONPATH
cd ${BASE_DIR} || exit
source bin/activate
export PYTHONPATH="${CODE_DIR}"
export DISPLAY="localhost:1"
alias python='$BASE_DIR/bin/python'


# Remove $LOG_FILE if already found.
if [ -f "$LOG_FILE" ]; then
    rm -f ${LOG_FILE} ${BOLLINGER_LOG_FILE}
fi

# Add new  $LOG_FILE
touch ${LOG_FILE} ${BOLLINGER_LOG_FILE}

DATE=`env TZ=US/Eastern date`
echo "$DATE" >> ${LOG_FILE}

for (( i = 0; i < ${#passwords[@]}; i++ )); do
    python "${CODE_DIR}/ibkrs/all_stocks.py" --username "${usernames[i]}" --passkey "${passwords[i]}"  \
           --account-id "${accounts[i]}" --stock-type "${ALL_STOCK}" >> ${LOG_FILE} 2>&1
    echo "$NEW_LINE" >> ${LOG_FILE}

    echo "Running Bollinger for account ${usernames[i]} ${accounts[i]} ..." >> ${BOLLINGER_LOG_FILE}
    python "${CODE_DIR}/ibkrs/bollinger_band.py" --username "${usernames[i]}" --account-id "${accounts[i]}"  >> ${BOLLINGER_LOG_FILE} 2>&1

    echo "Going to nap for ${NAP_SECONDS}sec.."
    sleep ${NAP_SECONDS}
done

echo "Finished!!"