#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\e[0;31m'
GREEN='\e[0;32m'
YELLOW='\e[0;33m'
NC='\e[0m'

# Banner setup

b1() {
    curl https://snips.sh/f/ZuwtQ3Pk0x?r=1
}

b2() {
    echo -e "-----------------------------------------------"
    echo -e "  Shell script to setup the following "
    echo -e "${GREEN}  uv add asyncio rich requests pytest-playwright  ${NC}"
    echo -e "${GREEN}  uvx playwright install --with-deps ${NC}"
    echo -e "-----------------------------------------------"
}

s1() {
    echo -e "${YELLOW} Executing ${NC}"
    uv add asyncio rich requests pytest-playwright
    uvx playwright install --with-deps
    uv tree
    echo -e "${YELLOW} Done ${NC}"
}

# Execution Sequence
b1 # Main Banner
b2 # Banner Text
s1
