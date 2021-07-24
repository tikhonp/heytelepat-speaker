#!/bin/bash

cd .. # Exit to root directory `heytelepat-speaker`

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_DEPENDENCIES=0
REQUIREMENTS="requirements.txt"
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
    sudo apt install portaudio19-dev libatlas-base-dev build-essential libssl-dev libffi-dev -y
    sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 -y
  } >/dev/null; then
    echo -e "   ${GREEN}[ OK ]${NC}"
  else
    echo -e "   ${RED}[ FAILED ]${NC}"
  fi

  echo -n "Installing python 3.9"
  ./install_python3.9.sh && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

  # Installing voice card driver ---------------------------

  echo -n "Installing voice card driver..."
  if {
    git clone https://github.com/respeaker/seeed-voicecard.git
    cd seeed-voicecard || exit
    sudo ./install.sh
    cd ..
    rm -rf seeed-voicecard
  } >/dev/null; then
    echo -e "   ${GREEN}[ OK ]${NC}"
  else
    echo -e "   ${RED}[ FAILED ]${NC}"
  fi

fi

# Creating python venv and installing pip dependencies

echo -n "Setting up python environment..."
if ((DEVELOPMENT == 1)); then
  echo -n -e "\n${YELLOW}Development mode. Setting python to \`python\` instead of \`python3.9\`...${NC}"
  python=python
else
  python=python3.9
fi
if {
  # shellcheck disable=SC2091
  $python -m venv env
  source env/bin/activate
  env/bin/pip install -U pip
} >/dev/null; then
  echo -e "   ${GREEN}[ OK ]${NC}"
else
  echo -e "   ${RED}[ FAILED ]${NC}"
fi

echo -n "Installing python requirements from \`$REQUIREMENTS\`, may take a while..."
if {
  env/bin/pip install -r "installation/$REQUIREMENTS" || exit
} >/dev/null; then
  echo -e "   ${GREEN}[ OK ]${NC}"
else
  echo -e "   ${RED}[ FAILED ]${NC}"
fi

# Creating systemd services --------

echo -n "Creating systemd services..."
cd installation || exit
mkdir services
../env/bin/python render_services.py "$USER" services && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
if ((DEVELOPMENT == 1)); then
  echo -e "${YELLOW}Development mode. Skipping setting up services...${NC}"
else
  echo -n "Putting generated units into \`/etc/systemd/system/\`..."
  sudo mv -v services/* /etc/systemd/system/ && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
  echo -n "Running daemon-reload..."
  sudo systemctl daemon-reload && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"
  rm -rf services
fi
cd ..

# UPDATING DEPRECATED TOKEN NEEDED
# Updating speaker to last version
#cd updater || exit
#../env/bin/python update.py --update_only || exit
#cd ..

if ((DEVELOPMENT == 1)); then
  echo -e "${YELLOW}Development mode. Skipping setting up script and enabling services...${NC}"
  exit
fi

# Granting SUDO to python executable scripts
echo -n "Granting SUDO to shell executable scripts..."
# Scripts: src/network/add_network.sh, src/network/connect_network.sh,
# updater/start_speaker_service.sh, updater/stop_speaker_service.sh,

if {
  sudo chown root:root src/network/add_network.sh src/network/connect_network.sh \
    updater/start_speaker_service.sh updater/stop_speaker_service.sh
  sudo chmod 700 src/network/add_network.sh src/network/connect_network.sh \
    updater/start_speaker_service.sh updater/stop_speaker_service.sh
}; then
  echo -e "   ${GREEN}[ OK ]${NC}"
else
  echo -e "   ${RED}[ FAILED ]${NC}"
fi

# Enabling system services ---------

echo -n "Enabling speaker service..."
sudo systemctl enable speaker && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Enabling speaker_updater service..."
sudo systemctl enable speaker_updater && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Starting speaker_updater service..."
sudo systemctl start speaker_updater && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

# shellcheck disable=SC1073
echo -e "${GREEN}Done!${NC} Please reboot system. To start speaker run \`sudo systemctl start speaker\`"
