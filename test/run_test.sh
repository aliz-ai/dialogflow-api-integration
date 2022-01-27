#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." &> /dev/null && pwd)"
VENV_DIR="${ROOT_DIR}/venv"

if [[ ! -f "${ROOT_DIR}/sa-key.json" ]] ; then
    echo "Error: Missing Google SA key file at: ${ROOT_DIR}/sa-key.json"
    exit 1
fi

if [[ ! -d "${VENV_DIR}" ]] ; then
    virtualenv -p python3 "${VENV_DIR}"
    ${VENV_DIR}/bin/pip install -U pip setuptools
    ${VENV_DIR}/bin/pip install -e "${ROOT_DIR}"
fi

export GOOGLE_APPLICATION_CREDENTIALS="${ROOT_DIR}/sa-key.json"
${VENV_DIR}/bin/chatbot --debug -p 8080 &

HABA_CHATBOT_PID=$!
trap "pkill -9 -P $HABA_CHATBOT_PID" 0

sleep 5

echo ""
echo ""
echo "Sending hello"
curl -X POST -H "Content-Type: application/json" -d @"${ROOT_DIR}/test/data_hello.json" http://localhost:8080/webhook

echo ""
echo ""
echo "Sending card number"
curl -X POST -H "Content-Type: application/json" -d @"${ROOT_DIR}/test/data_card_number.json" http://localhost:8080/webhook

echo ""
echo ""
echo "Sending no thanks x1"
curl -X POST -H "Content-Type: application/json" -d @"${ROOT_DIR}/test/data_no_thanks.json" http://localhost:8080/webhook

echo ""
echo ""
echo "Sending no thanks x2"
curl -X POST -H "Content-Type: application/json" -d @"${ROOT_DIR}/test/data_no_thanks.json" http://localhost:8080/webhook

echo ""
echo ""
