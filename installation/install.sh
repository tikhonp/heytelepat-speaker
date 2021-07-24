#!/bin/bash

cd .. # Exit to root directory `heytelepat-speaker`

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
  echo "Skipping apt-get dependencies installation..."
else
  # Installing all apt-get dependencies -------------------------------------------------------

  echo "Installing all apt-get dependencies..."
  {
    sudo apt update
    sudo apt install portaudio19-dev libatlas-base-dev build-essential libssl-dev libffi-dev -y
    sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 -y
  } &>/dev/null

  echo "Installing python 3.9"
  ./install_python3.9.sh

  # Installing voice card driver ---------------------------

  echo "Installing voice card driver..."
  {
    git clone https://github.com/respeaker/seeed-voicecard.git
    cd seeed-voicecard || exit
    sudo ./install.sh
    cd ..
    rm -rf seeed-voicecard
  } &>/dev/null

fi

# Creating python venv and installing pip dependencies

echo "Setting up python environment..."
{
  python3.9 -m venv env
  source env/bin/activate
  env/bin/pip install -U pip
} &>/dev/null

echo "Installing python requirements from \`$REQUIREMENTS\`..."
{
  env/bin/pip install -r "installation/$REQUIREMENTS" || exit
} &>/dev/null

# Creating systemd services --------

echo "Creating systemd services..."
cd installation || exit
mkdir services
../env/bin/python render_services.py "$USER" services || exit
if ((DEVELOPMENT == 1)); then
  echo "Development mode. Skipping setting up services..."
else
  sudo mv -v services/* /etc/systemd/system/ || exit
  sudo systemctl daemon-reload || exit
  rm -rf services
fi
cd ..

# Updating speaker to last version

cd updater || exit
../env/bin/python update.py --update_only || exit
cd ..

if ((DEVELOPMENT == 1)); then
  echo "Development mode. Skipping setting up script and enabling services..."
  exit
fi

# Granting SUDO to python executable scripts

# Scripts: src/network/add_network.sh, src/network/connect_network.sh,
# updater/start_speaker_service.sh, updater/stop_speaker_service.sh,

sudo chown root:root src/network/add_network.sh src/network/connect_network.sh \
  updater/start_speaker_service.sh updater/stop_speaker_service.sh
sudo chmod 700 src/network/add_network.sh src/network/connect_network.sh \
  updater/start_speaker_service.sh updater/stop_speaker_service.sh

# Enabling system services ---------

sudo systemctl enable speaker
sudo systemctl enable speaker_updater

sudo systemctl start speaker_updater

# shellcheck disable=SC1073
echo "Done! Please reboot system. To start speaker run \`sudo systemctl start speaker\`"
