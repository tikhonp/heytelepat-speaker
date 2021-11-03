#!/usr/bin/env python

"""
`issue_manager.py`
Commit speaker log util
OOO Telepat, All Rights Reserved
"""

__version__ = '0.0.1'
__author__ = 'Tikhon Petrishchev'
__credits__ = 'TelePat LLC'

import configparser
import json
import logging
import subprocess
from pathlib import Path

import requests
import websockets
from cysystemd.daemon import notify, Notification

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILENAME = os.path.join(BASE_DIR, 'src/settings.ini')
config_filename = os.path.join(Path.home(), '.speaker/config.json')


def get_settings():
    """Load ini config and generates dictionary"""

    global SETTINGS_FILENAME

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


async def on_message(host: str, issue_id: int, token: str):
    global BASE_DIR

    file_path = os.path.join(BASE_DIR, 'issue_manager', f'issue_{issue_id}.log')

    subprocess.run(
        ['sudo', 'journalctl', '-u', 'speaker', '>', file_path],
        stdout=subprocess.PIPE
    )

    url = f'https://{host}/staff/issue/log/{issue_id}/{token}/'
    with open(file_path, 'rb') as f:
        files = {'upload_file': f}
        answer = requests.post(url, files=files)

    answer.raise_for_status()


async def websocket_connect(host: str, token: str):
    url = f'wss://{host}/ws/staff/issue/'
    init_message = {'token': token}

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps(init_message))
            while True:
                if message := self.decode_json(await ws.recv()):
                    await on_message(host, message.get('id'), token)
    except websockets.exceptions.ConnectionClosedError:
        return


async def main():
    settings = get_settings()
    while True:
        await websocket_connect(settings.get('SERVER').get('HOST'), get_token())


notify(Notification.READY)
asyncio.run(main())
