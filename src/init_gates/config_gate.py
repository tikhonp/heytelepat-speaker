import asyncio
import configparser
import functools
import json
import os
import traceback
from pathlib import Path

import requests
from speechkit import Session
from speechkit.auth import generate_jwt

from core import pixels, sound_processor
from core.speech import (
    PlaySpeech,
    ListenRecognizeSpeech,
    raspberry_simple_audio_play_audio_function,
    default_play_audio_function
)
from core.speaker_logging import get_logger

logger = get_logger()


class ObjectStorage:
    """Stores all objects for speaker functioning"""

    def __init__(self, config, **kwargs):
        """
        :param dict config: Data from speaker_config.json file
        :param string config_filename: File path to config

        :param function input_function: Function that captures voice action, default `lambda: input("Press enter.")`
        :param string CONFIG_FILENAME: Path to config file, default `~/.speaker/config.json`
        :param boolean development: If development mode, default `False`
        :param boolean debug_mode: Debug mode status, default `None`
        :param string cash_filename: File path of cash file, default get from config
        :param string version: Version of script like `major.minor.fix`, default `null`

        :return: __init__ should return None
        :rtype: None
        """

        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.config = config

        self.inputFunction = kwargs.get('input_function')
        self.config_filename = kwargs.get('CONFIG_FILENAME', os.path.join(Path.home(), '.speaker/config.json'))
        self.development = kwargs.get('development', False)
        self.debug_mode = kwargs.get('debug_mode')
        self.cash_filename = kwargs.get('cash_filename', os.path.join(Path.home(), '.speaker/speech.cash'))
        self.version = kwargs.get('version', 'null')
        self.serial_no = get_serial_no()

        self.event_loop = asyncio.get_event_loop()
        # self.event_loop.set_exception_handler(self.handle_exception)

        self.pixels = pixels.Pixels(self.development)
        try:
            self.session = Session.from_jwt(self.speechkit_jwt_token())
        except requests.exceptions.ConnectionError:
            self.session = None

        self.play_speech = PlaySpeech(self.session, self.cash_filename, self.pixels)

        if self.session:
            self.listen_recognize_speech = ListenRecognizeSpeech(self.session, self.pixels)

        self.auth_code = None
        """Stores code if first authentication."""

    def init_speechkit(self):
        self.session = Session.from_jwt(self.speechkit_jwt_token())
        play_audio_function = default_play_audio_function if self.development else \
            raspberry_simple_audio_play_audio_function
        self.play_speech = PlaySpeech(self.session, self.cash_filename, self.pixels, play_audio_function)
        self.listen_recognize_speech = ListenRecognizeSpeech(self.session, self.pixels)

    def save_config(self):
        """Save config property to json file."""

        save_config(self.config, self.config_filename)

    def reset_token(self):
        """Puts token to null and saves config"""

        logger.info("Resetting token...")

        if self.token is None:
            logger.warning("Token don't exist")
            return

        requests.delete(self.host_http + 'speaker/', json={'token': self.token}).raise_for_status()

        self.config['token'] = None
        if 'token' in self.__dict__:
            del self.__dict__['token']
        self.save_config()

    def handle_exception(self, loop, context):
        """Loop exception handler."""

        loop.default_exception_handler(context)

        _ = context.get('exception')

        if self.development:
            answer = requests.post(self.host_http + 'exception/', json={
                'token': self.token,
                'traceback': str(context) + '\n\nException:\n' + str(
                    context.get('exception')) + '\nTraceback:\n' + traceback.format_exc()
            })

            if not answer.ok:
                logger.error("Failed to push error to server, {}, {}".format(
                    answer.status_code, answer.text
                ))

        logger.error("Handling exception... {}".format(context))
        loop.stop()

    @staticmethod
    def _get_location_data():
        answer = requests.get('https://ipinfo.io/json')
        if answer.ok:
            return answer.json()
        else:
            return {}

    def speechkit_jwt_token(self):
        """
        JWT token for speechkit

        :return: Jwt token or None if not found
        :rtype: str | None
        """
        private_key_filename = os.path.join(
            self.BASE_DIR, self.config.get('speechkit_private_key_filename')
        )
        with open(private_key_filename, 'rb') as f:
            private_key = f.read()
        return generate_jwt(
            self.config.get('speechkit_service_account_id'),
            self.config.get('speechkit_key_id'),
            private_key
        )

    @functools.cached_property
    def host(self):
        """
        Host of heytelepat-server

        :return: Host in format domain only like 'google.com'
        :rtype: string | None
        """
        return self.config.get('host')

    @functools.cached_property
    def host_http(self, prefix='https://', postfix='/speaker/api/v1/'):
        """
        URL for HTTP requests

        :param string prefix: HTTP prefix, default `https://`
        :param string postfix: Base API url, default `/speaker/api/v1/`
        :return: Full URL for http request, like `https://domain.com/speaker/api/v1/`,
        if `ObjectStorage.host` is not None
        :rtype: string | None
        """
        return prefix + self.host + postfix if self.host else None

    @functools.cached_property
    def host_ws(self, prefix='wss://', postfix='/ws/speakerapi/'):
        """
        URL for websockets requests

        :param string prefix: HTTP prefix, default `wss://`
        :param string postfix: Base API url, default `/ws/speakerapi/`
        :return: Full URL for websocket request, like `wss://domain.com/`
        :rtype: string
        """
        return prefix + self.host + postfix if self.host else None

    @functools.cached_property
    def token(self):
        """
        Token of heytelepat-speaker server, to reset cash call `del ObjectStorage.token`

        :rtype: string | None
        """
        return self.config.get('token')

    @functools.cached_property
    def weather_token(self):
        return self.config.get('weather_token')

    @functools.cached_property
    def city(self):
        return self._get_location_data().get('city')

    @functools.cached_property
    def region(self):
        return self._get_location_data().get('region')

    @functools.cached_property
    def country(self):
        return self._get_location_data().get('country')

    @functools.cached_property
    def timezone(self):
        return self._get_location_data().get('timezone')


def get_settings():
    """
    Load ini config and generates dictionary

    :rtype: dict
    """
    logger.info("First loading from `settings.ini`")
    settings_filename = os.path.join(Path(__file__).resolve().parent.parent, 'settings.ini')

    if not Path(settings_filename).resolve().is_file():
        raise FileNotFoundError("No such file or directory: '{}'".format(settings_filename))

    config = configparser.ConfigParser()
    config.read(settings_filename)

    return {
        'speechkit_service_account_id': config['SPEECHKIT']['SERVICE_ACCOUNT_ID'],
        'speechkit_key_id': config['SPEECHKIT']['KEY_ID'],
        'speechkit_private_key_filename': config['SPEECHKIT']['PRIVATE_KEY_FILENAME'],
        'host': config['SERVER']['HOST'],
        'version': config['GLOBAL']['VERSION'],
        'weather_token': config['WEATHER']['TOKEN']
    }


def save_config(config: dict, file_path: str):
    logger.info("Saving config to `{}`".format(file_path))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(config, f)


def load_config(file_path):
    """
    Load config file if exists

    :param string file_path: Path to config file
    :return: Optional python dict with config
    :rtype: dict | None
    """
    try:
        with open(file_path) as f:
            config = json.load(f)
        logger.info("Loaded config with filename `{}`".format(file_path))
        return config
    except FileNotFoundError:
        return


def get_serial_no():
    """
    Get serial number stored in file in root

    :return: serial number
    :rtype: str | None
    """

    # TODO проверить имя файла

    file_path = os.path.join(Path.home(), '.serial_no')
    try:
        with open(file_path) as f:
            serial_no = f.read().strip()
        logger.info("Loaded serial no ({}) with filename `{}`".format(
            serial_no, file_path
        ))
        return serial_no
    except FileNotFoundError:
        logger.error("Serial no not found in `{}`".format(file_path))
        return


def config_gate(
        input_function,
        debug_mode=False,
        reset=False,
        clean_cash=False,
        development=False,
        version=None
):
    """Default config file stores in ~/.speaker/config.json"""

    config_file_path = os.path.join(Path.home(), '.speaker/config.json')

    if not (config := load_config(config_file_path)):
        config = get_settings()
        config['token'] = None
    else:
        config.update(get_settings())

    save_config(config, config_file_path)

    if input_function == 'rpi_button':
        logger.info("Setup input function as Button")
        input_function = sound_processor.raspberry_input_function
    elif input_function == 'wake_up_word':
        logger.info("Setup wake_up_word input function")
        input_function = sound_processor.wakeup_word_input_function
    elif input_function == 'simple':
        logger.info("Setup input simple input function")
        input_function = sound_processor.async_simple_input_function
    else:
        raise ValueError(
            "Invalid input fiction '{}'. ".format(input_function) +
            "Available options: ['simple', 'rpi_button', 'wake_up_word']")

    object_storage = ObjectStorage(
        config,
        input_function=input_function,
        config_filename=config_file_path,
        development=development,
        debug_mode=debug_mode,
        version=version
    )

    if reset:
        object_storage.reset_token()

    if object_storage.version != config.get('version'):
        raise ValueError("Main file version ({}) and config version ({}) didn't match!".format(
            object_storage.version, config.get('version')))

    if clean_cash:
        logger.info("Cleanup cash")
        object_storage.play_speech.reset_cash()

    return object_storage
