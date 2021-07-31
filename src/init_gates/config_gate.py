import configparser
import functools
import json
import logging
import os
from pathlib import Path

import requests

from core import speech, pixels, soundProcessor


class ObjectStorage:
    """Stores all objects for speaker functioning"""

    def __init__(self, config, **kwargs):
        """
        :param dict config: Data from speaker_config.json file
        :param string config_filename: File path to config

        :param function input_function: Function that captures voice action, default `lambda: input("Press enter.")`
        :param string config_filename: Path to config file, default `~/.speaker/config.json`
        :param boolean development: If development mode, default `False`
        :param boolean debug_mode: Debug mode status, default `None`
        :param string cash_filename: File path of cash file, default get from config
        :param pixels.Pixels pixels: Object of pixels class default initialises
        :param function play_audio_function: Function to play audio BytesIO, default `speech.play_audio_function`
        :param speech.Speech speech_cls: Object of Speech class, default initialises (`play_audio_function` required)
        :param speech.SpeakSpeech speakSpeech_cls: Object of SpeakSpeech class, default initialises
        :param string version: Version of script like `major.minor.fix`, default `null`

        :return: __init__ should return None
        :rtype: None
        """

        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.config = config

        self.inputFunction = kwargs.get('input_function', lambda: input("Press enter."))
        self.config_filename = kwargs.get('config_filename', os.path.join(Path.home(), '.speaker/config.json'))
        self.development = kwargs.get('development', False)
        self.debug_mode = kwargs.get('debug_mode')
        self.cash_filename = kwargs.get('cash_filename', os.path.join(Path.home(), '.speaker/speech.cash'))
        self.pixels = kwargs.get('pixels', pixels.Pixels(self.development))
        self.play_audio_function = kwargs.get('play_audio_function', speech.play_audio_function)
        self.version = kwargs.get('version', 'null')

        if 'speech_cls' in kwargs:
            self.speech = kwargs['speech_cls']
        else:
            if self.play_audio_function is None:
                raise Exception("You must provide play_audio_function")
            self.speech = speech.Speech(self)

        self.speakSpeech = kwargs.get(
            'speakSpeech_cls', speech.SpeakSpeech(self.speech, self.cash_filename, self.pixels)
        )

    @staticmethod
    def _get_location_data():
        answer = requests.get('http://ipinfo.io/json')
        if answer.ok:
            return answer.json()
        else:
            return {}

    @functools.cached_property
    def api_key(self):
        return self.config.get('api_key')

    @functools.cached_property
    def catalog(self):
        return self.config.get('catalog')

    @functools.cached_property
    def host(self):
        return self.config.get('host')

    @functools.cached_property
    def host_http(self):
        return 'http://' + self.host + '/speaker/api/v1/' if self.host else None

    @functools.cached_property
    def host_ws(self):
        return 'ws://' + self.host if self.host else None

    @functools.cached_property
    def token(self):
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
    """Load ini config and generates dictionary

    :rtype: dict
    """

    logging.info("First loading from `settings.ini`")
    settings_filename = os.path.join(Path(__file__).resolve().parent.parent, 'settings.ini')

    if not Path(settings_filename).resolve().is_file():
        raise FileNotFoundError("No such file or directory: '{}'".format(settings_filename))

    config = configparser.ConfigParser()
    config.read(settings_filename)

    return {
        'api_key': config['SPEECHKIT']['API_KEY'],
        'catalog': config['SPEECHKIT']['CATALOG'],
        'host': config['SERVER']['HOST'],
        'version': config['GLOBAL']['VERSION'],
        'weather_token': config['WEATHER']['TOKEN']
    }


def save_config(config: dict, file_path: str):
    logging.info("Saving config to `{}`".format(file_path))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(config, f)


def load_config(file_path):
    """Load config file if exists

    :param string file_path: Path to config file
    :return: Optional python dict with config
    :rtype: dict | None
    """

    try:
        with open(file_path) as f:
            config = json.load(f)
        logging.info("Loaded config with filename `{}`".format(file_path))
        return config
    except FileNotFoundError:
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

    if reset:
        logging.info("Resetting token")
        config['token'] = None

    save_config(config, config_file_path)

    if input_function == 'rpi_button':
        logging.info("Setup input function as Button")
        input_function = soundProcessor.raspberry_input_function
    elif input_function == 'wake_up_word':
        logging.info("Setup wake_up_word input function")
        input_function = soundProcessor.wakeup_word_input_function
    elif input_function == 'simple':
        logging.info("Setup input simple input function")
        input_function = soundProcessor.async_simple_input_function
    else:
        raise ValueError(
            "Invalid input fiction '{}'. ".format(input_function) +
            "Available options: ['simple', 'rpi_button', 'wake_up_word']")

    object_storage = ObjectStorage(
        config,
        input_function=input_function,
        config_filename=config_file_path,
        development=development,
        play_audio_function=speech.play_audio_function,
        debug_mode=debug_mode,
        version=version
    )

    if object_storage.version != config.get('version'):
        raise ValueError("Main file version ({}) and config version ({}) didn't match!".format(
            object_storage.version, config.get('version')))

    if clean_cash:
        logging.info("Cleanup cash")
        object_storage.speakSpeech.reset_cash()

    return object_storage
