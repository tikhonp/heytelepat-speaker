#!/bin/sh
sudo wpa_cli -i wlan0 reconfigure || (
  sudo systemctl daemon-reload
  sudo systemctl restart dhcpcd
  sudo wpa_cli -i wlan0 reconfigure
)
