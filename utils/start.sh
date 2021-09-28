#!/bin/bash
echo "Running....."

BASE_DIR="/home/ec2-user/virenv"
CODE_DIR="$BASE_DIR/pcv"
SERVER_DIR="$BASE_DIR/pcv/clientportal"

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

echo "Finished!!"