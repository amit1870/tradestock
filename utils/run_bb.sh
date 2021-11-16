#!/bin/bash
echo "Running....."

BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
RESOURCE_DIR="$CODE_DIR/resources"
BOLLINGER_STREAM_LOG="$RESOURCE_DIR/bbstream.log"
LONG_SLEEP=1800 # Seconds

declare -a usernames=("peace77t6" "peace77t4" "peace77t3")
declare -a accounts=("U6092014" "U6498436" "U7242803")
declare -a passwords=( "$@" )

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

i=0
ARRAY_LEN=${#usernames[@]}

while :
do
    python "${CODE_DIR}/ibkrs/order_stream_bband.py" --username "${usernames[i]}" --passkey "${passwords[i]}"  \
           --account-id "${accounts[i]}" & >> /dev/null 2>&1

    echo "Going to long sleep for ${LONG_SLEEP}sec.."
    sleep ${LONG_SLEEP}

    echo "Going to kill above python process ..."
    kill $(ps aux | grep "[o]rder_stream_bband.py" | awk '{print $2}')
    echo "Killed !"

    ((i=i+1))

    if [[ $i -eq $ARRAY_LEN ]]; then
        ((i=0))
    fi

done

echo "Finished!!"