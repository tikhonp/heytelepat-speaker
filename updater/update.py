#!/usr/bin/env python

"""
`updater.py`
Update speaker firmware util
OOO Telepat, All Rights Reserved
"""

__version__ = '0.0.2'
__author__ = 'Tikhon Petrishchev'
__credits__ = 'TelePat LLC'

import argparse
import configparser
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent

settings_filename = os.path.join(BASE_DIR, 'src/settings.ini')
config_filename = os.path.join(Path.home(), '.speaker/config.json')


def install_pip_req(requirements_file):
    logging.info("Installing pip requirements...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])


def get_settings():
    """Load ini config and generates dictionary"""
    global settings_filename

    with open(settings_filename):
        pass

    config = configparser.ConfigParser()
    config.read(settings_filename)
    logging.info("Loaded settings from `{}`.".format(settings_filename))
    return config


def get_token():
    """Load token if exists

    :return: string token if exists
    :rtype: str | None
    """

    global config_filename
    try:
        with open(config_filename) as f:
            config = json.load(f)
            return config.get('token')
    except FileNotFoundError:
        logging.warning("Config not found in `{}`.".format(config_filename))
        return


def check_if_new_version_available():
    """Get new version if exists

    :return: String version if exists
    :rtype: str | None
    """

    if not (token := get_token()):
        logging.warning("Token does not exists.")
        return
    logging.info("Loaded token.")

    settings = get_settings()
    version = settings['GLOBAL']['VERSION']
    host = settings['SERVER']['HOST']

    answer = requests.get('http://' + host + '/speaker/api/v1/speaker/', json={'token': token})
    answer.raise_for_status()
    server_version = answer.json().get('version')
    if server_version != version:
        raise ValueError(
            "Version on server ({}) and settings.ini ({}) don't match.".format(server_version, version))
    logging.info("Current version detected `{}`.".format(version))

    answer = requests.post('http://' + host + '/speaker/api/v1/firmware/', json={'token': token})
    answer.raise_for_status()
    return answer.json().get('new_firmware')


def update_firmware(version: str):
    global BASE_DIR
    token = get_token()
    host = get_settings()['SERVER']['HOST']

    answer = requests.get('http://' + host + '/speaker/api/v1/firmware/', json={'token': token, 'version': version})
    answer.raise_for_status()

    url = 'http://' + host + answer.json().get('data')
    with requests.get(url, stream=True) as answer:
        answer.raise_for_status()

        filename = url.split('/')[-1]
        tar_firmware_path = os.path.join(BASE_DIR, 'updater', filename)
        logging.info("Downloading firmware into `{}`...".format(tar_firmware_path))
        with open(tar_firmware_path, 'wb') as f:
            for chunk in answer.iter_content():
                f.write(chunk)

    firmware_directory = os.path.join(BASE_DIR, 'updater', 'src')
    logging.info("Unpacking `{}` into `{}`...".format(filename, firmware_directory))
    with tarfile.open(tar_firmware_path) as tar:
        tar.extractall(os.path.join(BASE_DIR, 'updater'))
    os.remove(tar_firmware_path)

    source_firmware_path = os.path.join(BASE_DIR, 'src')
    logging.info("Removing old firmware...")
    shutil.rmtree(source_firmware_path, ignore_errors=True)
    logging.info("Moving new firmware to `src`.")
    shutil.move(firmware_directory, source_firmware_path)


def main(dev=False):
    global BASE_DIR

    if not (version := check_if_new_version_available()):
        logging.info("New firmware not found, stopping...")
        return
    logging.info("New firmware available `{}`.".format(version))

    if not dev:
        logging.info("Stopping speaker service...")
        os.system('sudo {}'.format(os.path.join(BASE_DIR, 'updater', 'stop_speaker_service.sh')))

    update_firmware(version)

    if not dev:
        install_pip_req(os.path.join(BASE_DIR, 'src', 'requirements.txt'))

    cash_path = os.path.join(Path.home(), '.speaker/speech.cash')
    if Path(cash_path).resolve().is_file():
        logging.info("Removing cash...")
        os.remove(cash_path)

    logging.info("Storing init cash...")
    command = [os.path.join(BASE_DIR, 'env', 'bin', 'python'), os.path.join(BASE_DIR, 'src', 'speaker.py'),
               '--store_cash']
    if dev:
        command.append('-d')
    subprocess.check_call(command)

    logging.info("Done! Successfully updated to `{}`.".format(version))

    if not dev:
        logging.info("Starting speaker service...")
        os.system('sudo {}'.format(os.path.join(BASE_DIR, 'updater', 'start_speaker_service.sh')))


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser(description="Update speaker firmware util.")
    parser.add_argument('-d', '--development', help="Dev mode, run updates without restarting speaker service.",
                        action='store_true')
    args = parser.parse_args()
    logging.info("Update speaker firmware util [{}]. `OOO Telepat` All Rights Reserved.".format(__version__))
    try:
        main(dev=args.development)
    except requests.exceptions.ConnectionError:
        logging.warning("Internet connection unavailable, stopping...")
