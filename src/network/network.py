"""
Provides network checking and wireless connection for raspberrypi

Connection to network with this instruction:
    https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
"""

import logging
import subprocess

import requests


class Network:
    """Adding, deleting and connecting wireless network"""

    def __init__(self, ssid: str):
        self.ssid = ssid
        self.wpa_supplicant_filename = '/etc/wpa_supplicant/wpa_supplicant.conf'

    @staticmethod
    def _call_iw_scan() -> str:
        command = ['sudo', 'iw', 'dev', 'wlan0', 'scan']
        result = subprocess.run(command, stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')

    # DEPRECATED:
    # @staticmethod
    # def _parse_iw_scan(iw_data: str) -> list:
    #     networks = list()
    #     for line in iw_data.split('\n'):
    #         if line[:3] == 'BSS':
    #             networks.append({'bssid', line.split()[1].split('(')[0]})
    #         elif 'SSID' in line:
    #             networks[-1]['ssid'] = line.strip().split[1]
    #         elif 'Pairwise ciphers' in line:
    #             networks[-1]['pairwise'] = line.split(':')[1].strip()
    #
    #     return networks

    @property
    def available(self) -> bool:
        networks = self._call_iw_scan()
        logging.debug("Networks: {}".format(networks))
        return True if self.ssid in networks else False

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

        command = "wpa_passphrase \"{}\" {}".format(self.ssid, psk)
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')

        data = subprocess_return.split('\n')
        data.pop(2)

        for i in data:
            result = subprocess.run(['sudo', './network/add_network.sh', i], stdout=subprocess.PIPE)
            logging.debug("Result adding str: {}".format(result.stdout.decode('utf-8')))

    @staticmethod
    def connect() -> bool:
        result = subprocess.run(['sudo', './network/connect_network.sh'], stdout=subprocess.PIPE)
        subprocess_return = result.stdout.decode('utf-8')
        logging.debug("Connection return {}".format(subprocess_return))

        return True if 'OK' in subprocess_return else False


def check_connection_ping(host='google.com'):
    """Ping to host and if success return True else False

    :param string host: Host to ping, default 'google.com'
    :return: Connection exist or not
    :rtype: boolean
    """

    subprocess_return = subprocess.run(
        ['timeout', '1.5', 'ping', '-c', '1', host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return True if subprocess_return.returncode == 0 else False


def check_connection_get_request(host='https://google.com'):
    """Requests to host and if error return False else True

    :param string host: Host to request, default 'google.com'
    :return: Connection exist or not
    :rtype: boolean
    """

    try:
        requests.get(host)
        return True
    except requests.ConnectionError:
        logging.debug("Host connection error")
        return False
