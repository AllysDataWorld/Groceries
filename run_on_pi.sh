#!/bin/bash

###############################################
#  Color Definitions
###############################################
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
MAGENTA="\e[35m"
CYAN="\e[36m"
RESET="\e[0m"

###############################################
#  Banner
###############################################
echo "==============================================="
echo "        🚀 Starting Flask Application"
echo "==============================================="


###############################################
#  Check virtual environment
###############################################
if [ ! -d "AI" ]; then
    echo -e "${RED}❌ Virtual environment folder 'AI' not found.${RESET}"
    echo -e "${YELLOW}Create it with:${RESET}"
    echo "cd to GroceriesApp and use CMD:source AI/bin/activate"
    exit 1
fi

echo -e "${YELLOW}✔ Virtual environment found${RESET}"

APP_DIR="$(cd "$(dirname "$0")" && pwd)"  # always the script's own directory
source "$APP_DIR/../AI/bin/activate"
echo -e "${GREEN}✔ Virtual environment activated @ $VIRTUAL_ENV ${RESET}"
echo -e "Virtual Environment: $VIRTUAL_ENV"

###############################################
#  Check FLASK_ENV
###############################################
if [ -z "$FLASK_ENV" ]; then
    echo -e "${YELLOW}⚠ FLASK_ENV is not set. Defaulting to 'production'.${RESET}"
    export FLASK_ENV=production
fi

if [ "$FLASK_ENV" = "production" ]; then
    echo -e "${MAGENTA}🔥 Running in PRODUCTION mode${RESET}"
else
    echo -e "${YELLOW}🧪 Running in DEVELOPMENT mode${RESET}"
fi


###############################################
#  Start Flask
###############################################
echo -e "${CYAN}"
echo "-----------------------------------------------"
echo "🚀 Launching Flask..."
echo "-----------------------------------------------"
echo -e "${RESET}"

cd "$APP_DIR"
python3 run.py