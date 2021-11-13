#!/bin/bash
echo "Running....."

BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
RESOURCE_DIR="$CODE_DIR/resources"
BOLLINGER_STREAM_LOG="$RESOURCE_DIR/bbstream.log"
NAP_SECONDS=10 # Seconds
NEW_LINE=$'\n'

declare -a usernames=("peace77t3")
declare -a accounts=("U7242803")
declare -a password=$1
shift
declare -a conids=("$@")

# Activate vitural env and export PYTHONPATH
cd ${BASE_DIR} || exit
source bin/activate
export PYTHONPATH="${CODE_DIR}"
export DISPLAY="localhost:1"
alias python='$BASE_DIR/bin/python'


# Remove $BOLLINGER_STREAM_LOG if already found.
if [ -f "$BOLLINGER_STREAM_LOG" ]; then
    rm -f ${BOLLINGER_STREAM_LOG}
fi

# Add new $BOLLINGER_STREAM_LOG
touch ${BOLLINGER_STREAM_LOG}

for (( i = 0; i < ${#conids[@]}; i++ )); do

    if [[ $i -eq 0 ]]; then
        python "${CODE_DIR}/ibkrs/order_stream_bband.py" --username "${usernames[i]}" --account-id "${accounts[i]}" \
               --passkey "${password}" --conid "${conids[i]}"
    else
        python "${CODE_DIR}/ibkrs/order_stream_bband.py" --username "${usernames[i]}" --account-id "${accounts[i]}" --conid "${conids[i]}"
    fi

    echo "Going to nap for ${NAP_SECONDS}sec.."
    sleep ${NAP_SECONDS}

done

echo "Finished!!"