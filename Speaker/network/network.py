"""
Provides network checking and wireliss connection for raspberrypi

Connection to network with this instruction:
    https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
"""

import subprocess
import socket
import urllib.request


class Network:
    def __init__(self, ssid: str):
        self.ssid = ssid

    def check_available(self) -> bool:
        command = "sudo iwlist wlan0 scan"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        if self.ssid in subprocess_return:
            return True
        else:
            return False

    def create(self, psk: str):
        if len(psk) < 8 or len(psk) > 63:
            raise Exception("Passphrase must be 8..63 characters")

        command = "wpa_passphrase {} {}".format(self.ssid, psk)
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        data = subprocess_return.split('\n')
        data.pop(2)

        for i in data:
            subprocess.run(['sudo', './network/add_network.sh', i])


    def connect(self):
        result = subprocess.run(['sudo', './network/connect_network.sh'], stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        if 'OK' in subprocess_return:
            return True
        else:
            return False


def check_connection_hardware():
    IPaddress=socket.gethostbyname(socket.gethostname())
    if IPaddress=="127.0.0.1":
        return False
    else:
        return True

def check_really_connection(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
