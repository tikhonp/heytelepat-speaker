import configparser
import json
import logging
import os
import threading
from pathlib import Path
from typing import Union

from utils import speech, pixels, soundProcessor


class ObjectStorage:
    """Stores all objects for speaker functioning"""

    def __init__(self, config, input_function, config_filename, **kwargs):
        """
        :param dict config: Data from speaker_config.json file
        :param function input_function: Function that captures voice action
        :param string config_filename: File path to config

        :param boolean development: If development mode, default `False`
        :param boolean debug_mode: Debug mode status, default `None`
        :param string cash_filename: File path of cash file, default get from config
        :param pixels.Pixels pixels: Object of pixels class default initialises
        :param function play_audio_function: Function to play audio BytesIO, default `None`
        :param threading.Event event_obj: Event object for threading events, default initialises
        :param threading.RLock lock_obj: Lock object for threading Locks, default initialises
        :param speech.Speech speech_cls: Object of Speech class, default initialises (`play_audio_function` required)
        :param speech.SpeakSpeech speakSpeech_cls: Object of SpeakSpeech class, default initialises
        :param string version: Version of script like `major.minor.fix`, default `null`

        :return None:
        """
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.config = config
        self.inputFunction = input_function
        self.config_filename = config_filename

        self.development = kwargs.get('development', False)
        self.debug_mode = kwargs.get('debug_mode')
        self.cash_filename = kwargs.get('cash_filename', os.path.join(Path.home(), '.speaker/speech.cash'))
        self.pixels = kwargs.get('pixels', pixels.Pixels(self.development))
        self.play_audio_function = kwargs.get('play_audio_function')
        self.event_obj = kwargs.get('event_obj', threading.Event())
        self.lock_obj = kwargs.get('lock_obj', threading.RLock())
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

    @property
    def api_key(self):
        return self.config.get('api_key')

    @property
    def catalog(self):
        return self.config.get('catalog')

    @property
    def host(self):
        return self.config.get('host')

    @property
    def host_http(self):
        return 'http://' + self.host + '/speaker/api/v1/' if self.host else None

    @property
    def host_ws(self):
        return 'ws://' + self.host if self.host else None

    @property
    def token(self):
        return self.config.get('token')


def get_settings() -> dict:
    """Load ini config and generates dictionary"""

    logging.info("First loading from `settings.ini`")
    settings_filename = 'settings.ini'

    with open(settings_filename):
        pass

    config = configparser.ConfigParser()
    config.read(settings_filename)

    return {
        'api_key': config['SPEECHKIT']['API_KEY'],
        'catalog': config['SPEECHKIT']['CATALOG'],
        'host': config['SERVER']['HOST'],
        'version': config['GLOBAL']['VERSION'],
    }


def save_config(config: dict, file_path: str):
    logging.info("Saving config to `{}`".format(file_path))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(config, f)


def load_config(file_path: str) -> Union[dict, None]:
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
        input_function = soundProcessor.simple_input_function
    else:
        raise ValueError(
            "Invalid input fiction '{}'. ".format(input_function) +
            "Available options: ['simple', 'rpi_button', 'wake_up_word']")

    object_storage = ObjectStorage(
        config,
        input_function,
        config_file_path,
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