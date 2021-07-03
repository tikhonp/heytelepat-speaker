"""
Provides network checking and wireliss connection for raspberrypi

Connection to network with this instruction:
    https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
"""

import subprocess
import socket
import requests
import logging


class Network:
    def __init__(self, ssid: str):
        self.ssid = ssid
        self.wpa_supplicant_filename = '/etc/wpa_supplicant/wpa_supplicant.conf'

    def check_available(self) -> bool:
        command = "sudo iwlist wlan0 scan"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        if self.ssid in subprocess_return:
            return True
        else:
            return False

    def _delete_network_if_exist(self):
        with open(self.wpa_supplicant_filename) as f:
            data = f.read()

        if self.ssid not in data:
            return

        data = data.split('network')
        del_i = 0
        for i, item in enumerate(data):
            if self.ssid in item:
                del_i = i
        if del_i == 0:
            raise RuntimeError("Could not delete previous network")

        data.pop(del_i)
        data = 'network'.join(data)

        with open(self.wpa_supplicant_filename, 'w') as f:
            f.write(data)

    def create(self, psk: str):
        if len(psk) < 8 or len(psk) > 63:
            raise Exception("Passphrase must be 8..63 characters")

        self._delete_network_if_exist()

        command = "wpa_passphrase {} {}".format(self.ssid, psk)
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        data = subprocess_return.split('\n')
        data.pop(2)

        for i in data:
            subprocess.run(['sudo', './network/add_network.sh', i])

    def connect(self):
        result = subprocess.run(['sudo', './network/connect_network.sh'],
                                stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        if 'OK' in subprocess_return:
            return True
        else:
            return False


def check_connection_hardware():
    IPaddress = socket.gethostbyname(socket.gethostname())
    logging.debug("IPaddress %s", IPaddress)
    if IPaddress == '127.0.0.1':
        return False
    else:
        return True


def check_really_connection(host='http://google.com'):
    try:
        requests.get(host)
        return True
    except requests.ConnectionError:
        logging.debug("Host connection error")
        return False
