"""
Provides network checking and wireliss connection for raspberrypi

Connection to network with this instruction:
    https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
"""

import subprocess


class Network:
    def __init__(self, ssid: str):
        self.ssid = ssid

    def check_available(self) -> bool:
        command = "sudo iwlist wlan0 scan | grep ESSID"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        if self.ssid in subprocess_return:
            return True
        else:
            return False

    def create(self, psk: str):
        command = "wpa_passphrase air76 petrischev123321"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        data = subprocess_return.split('\n')
        data.pop(2)
        data = "\n".join(data)

        subprocess.run(['sudo', './network/add_network.sh', data])

    def connect(self):
        subprocess.run(['sudo', './network/connect_network.sh'])
