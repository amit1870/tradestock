#!/bin/bash
echo "Running....."

BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
RESOURCE_DIR="$CODE_DIR/resources"
BOLLINGER_STREAM_LOG="$RESOURCE_DIR/bbstream.log"
OLD_BOLLINGER_STREAM_LOG="$RESOURCE_DIR/bbstream.old.log"
SCRIPT_LOG="$RESOURCE_DIR/script.log"
LONG_SLEEP=600 # Seconds
LOG_SIZE=200000 # 2MB

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
    rm -f ${BOLLINGER_STREAM_LOG} ${SCRIPT_LOG}
fi

# Add new $BOLLINGER_STREAM_LOG
touch ${BOLLINGER_STREAM_LOG} ${SCRIPT_LOG}

i=0
ARRAY_LEN=${#usernames[@]}

while :
do
    # Check log file size and mv $BOLLINGER_STREAM_LOG when size is $LOG_SIZE
    if [ -f "$BOLLINGER_STREAM_LOG" ]; then
        CURRENT_LOG_SIZE=$(stat -c%s $BOLLINGER_STREAM_LOG)
        if (( CURRENT_LOG_SIZE > LOG_SIZE )); then

            RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S')
            echo "$RUN_TIME Moving log to new log file" >> ${SCRIPT_LOG}

            mv $BOLLINGER_STREAM_LOG $OLD_BOLLINGER_STREAM_LOG
            touch $BOLLINGER_STREAM_LOG
        fi
    else
        touch $BOLLINGER_STREAM_LOG
    fi

    RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$RUN_TIME Check if order_stream_bband.py is alredy running ..." >> ${SCRIPT_LOG}

    py_pid=$(ps aux | grep "[o]rder_stream_bband.py" | awk '{print $2}')

    if ! [ -z "${py_pid}" ];then

        kill ${py_pid}

        RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$RUN_TIME Already running order_stream_bband.py killed with pid ${py_pid}." >> ${SCRIPT_LOG}

        sleep 1
    fi

    RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$RUN_TIME Starting order_stream_bband.py..." >> ${SCRIPT_LOG}

    python "${CODE_DIR}/ibkrs/order_stream_bband.py" --username "${usernames[i]}" --passkey "${passwords[i]}"  \
           --account-id "${accounts[i]}" & >> /dev/null 2>&1

    py_pid=$(ps aux | grep "[o]rder_stream_bband.py" | awk '{print $2}')

    if ! [ -z "${py_pid}" ];then

        RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$RUN_TIME Script order_stream_bband.py is running with pid ${py_pid}." >> ${SCRIPT_LOG}
        echo "$RUN_TIME Going to sleep for ${LONG_SLEEP}sec.." >> ${SCRIPT_LOG}

        sleep ${LONG_SLEEP}
    fi

    ((i=i+1))

    if [[ $i -eq $ARRAY_LEN ]]; then
        ((i=0))
    fi

done

echo "Finished!!"