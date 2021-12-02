#!/bin/bash

cd .. # Exit to root directory `heytelepat-speaker`

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_DEPENDENCIES=0
REQUIREMENTS="src/requirements.txt"
DEVELOPMENT=0
while getopts "h?sdr:" opt; do
  case "$opt" in
  h | \?)
    echo "usage: ./install.sh [-h] [-s] [-d] [-r REQUIREMENTS]"
    exit 0
    ;;
  s)
    SKIP_DEPENDENCIES=1
    ;;
  d)
    DEVELOPMENT=1
    ;;
  r)
    REQUIREMENTS=$OPTARG
    ;;
  esac
done

shift $((OPTIND - 1))

[ "${1:-}" = "--" ] && shift

if ((SKIP_DEPENDENCIES == 1)); then
  echo -e "${YELLOW}Skipping apt-get dependencies installation...${NC}"
else
  # Installing all apt-get dependencies -------------------------------------------------------

  echo -n "Installing all apt-get dependencies..."

  if {
    sudo apt update
    sudo apt install portaudio19-dev libatlas-base-dev \
      build-essential libssl-dev libffi-dev \
      libportaudio0 libportaudio2 \
      libportaudiocpp0 libasound2-plugins \
      python3 python3-dev python3-venv python3-pip -y
  }; then
    echo -e "   ${GREEN}[ OK ]${NC}"
  else
    echo -e "   ${RED}[ FAILED ]${NC}"
  fi

  # Installing voice card driver ---------------------------

  echo "Installing voice card driver..."
  if {
    git clone https://github.com/respeaker/seeed-voicecard.git
    cd seeed-voicecard || exit
    sudo ./install.sh
    cd ..
    rm -rf seeed-voicecard
  }; then
    echo -e "   ${GREEN}[ OK ]${NC}"
  else
    echo -e "   ${RED}[ FAILED ]${NC}"
  fi
fi

# Creating python venv and installing pip dependencies

echo -n "Setting up python environment..."
python=python3.9
{
  # shellcheck disable=SC2091
  $python -m venv env
  source env/bin/activate
  env/bin/pip install -U pip
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Installing python requirements from \`$REQUIREMENTS\`, may take a while..."


env/bin/pip install -r "$REQUIREMENTS" && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"c
