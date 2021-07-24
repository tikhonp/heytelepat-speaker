#!/bin/bash

RED='\033[1;31m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

echo -n "Stopping and deactivating speaker and speaker_updater services..."
{
  sudo systemctl stop speaker
  sudo systemctl stop speaker_updater.timer
  sudo systemctl stop speaker_updater

  sudo systemctl disable speaker
  sudo systemctl disable speaker.timer
  sudo systemctl disable speaker_updater
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Removing services units..."
{
  sudo rm /etc/systemd/system/speaker.service /etc/systemd/system/speaker_updater.service /etc/systemd/system/speaker_updater.timer
} >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Running daemon-reload..."
sudo systemctl daemon-reload && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -n "Removing config and cash files..."
rm -f ~/.speaker/config.json ~/.speaker/speech.cash >/dev/null && echo -e "   ${GREEN}[ OK ]${NC}" || echo -e "   ${RED}[ FAILED ]${NC}"

echo -e "${GREEN}Done!${NC} Heytelepat-speaker successfully uninstalled. Don't forget to remove \`heytelepat-speaker\` directory."

