import threading
from utils import speech, pixels
import soundProcessor
import json
import logging
from pathlib import Path
import os.path


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

        :return None:
        """
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.config = config
        self.inputFunction = input_function
        self.config_filename = config_filename

        self.development = kwargs.get('development', False)
        self.debug_mode = kwargs.get('debug_mode')
        self.cash_filename = kwargs.get('cash_filename', os.path.join(self.BASE_DIR, self.config['cash_filename']))
        self.pixels = kwargs.get('pixels', pixels.Pixels(self.development))
        self.play_audio_function = kwargs.get('play_audio_function')
        self.event_obj = kwargs.get('event_obj', threading.Event())
        self.lock_obj = kwargs.get('lock_obj', threading.RLock())

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
        return self.config['api_key']

    @property
    def catalog(self):
        return self.config['catalog']

    @property
    def host(self):
        return self.config['host']

    @property
    def token(self):
        return self.config['token']


def config_gate(
        config_filename,
        input_function,
        debug_mode=False,
        reset=False,
        clean_cash=False,
        development=False):

    with open(config_filename) as f:
        config = json.load(f)
    logging.info("Loaded config with filename '%s'", config_filename)

    if reset:
        logging.info("Resetting token")
        config['token'] = None
        with open(config_filename, 'w') as f:
            json.dump(config, f)

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
        config_filename,
        development=development,
        play_audio_function=speech.play_audio_function,
        debug_mode=debug_mode,
    )

    if clean_cash:
        logging.info("Cleanup cash")
        object_storage.speakSpeech.reset_cash()

    return object_storage
