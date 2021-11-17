#!/bin/bash
echo "Running setup....."

BASE_DIR="$HOME/virenv"
CODE_DIR="$BASE_DIR/pcv"
SERVER_DIR="$BASE_DIR/pcv/clientportal"
RESOURCE_DIR="$CODE_DIR/resources"
SETUP_LOG="$RESOURCE_DIR/setup.log"

# Create resources dir
mkdir -p ${RESOURCE_DIR}

# touch $SETUP_LOG if not found.
if ! [ -f "$SETUP_LOG" ]; then
    touch ${SETUP_LOG}
fi

# put current date as yyyy-mm-dd HH:MM:SS in $date
RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Run IBKR gateway if not running
java_pid=$(pidof java)
if ! [ -n "${java_pid}" -a "$java_pid" -ge 0 ];then
    cd ${SERVER_DIR} || exit
    echo "${RUN_TIME} Starting IBKR gateway..." >> ${SETUP_LOG} 2>&1
    nohup ./bin/run.sh root/conf.yaml >/dev/null 2>&1 &
    sleep 5

    java_pid=$(pidof java)
    if [ -n "${java_pid}" -a "$java_pid" -ge 0 ];then
        echo "${RUN_TIME} IBKR gateway is running with pid ${java_pid}."
    else
        echo "${RUN_TIME} IBKR gateway is not started. Please check with admin."
    fi
else
    echo "${RUN_TIME} IBKR gateway is running with pid ${java_pid}."
fi

# Activate vitural env and export PYTHONPATH
echo "${RUN_TIME} Activating virenv environment..."
cd ${BASE_DIR} || exit
source bin/activate
export PYTHONPATH="${CODE_DIR}"
export DISPLAY="localhost:1"
alias python='$BASE_DIR/bin/python'

echo "Finished!!"