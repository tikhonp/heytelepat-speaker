import threading
from utils import speech, pixels
import soundProcessor
import json
import logging
from pathlib import Path
import os.path


class ObjectStorage:
    def __init__(
        self,
        config,
        inputFunction,
        config_filename,
        development,
        **kwargs
    ):
        """
        kwargs:
            - lock_obj
            - event_obj
            - speech_cls
            - playaudiofunction
            - speakSpeech_cls
        """
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.config = config
        self.inputFunction = inputFunction
        self.config_filename = config_filename

        if 'cash_filename' in kwargs:
            self.cash_filename = kwargs['cash_filename']
        else:
            self.cash_filename = os.path.join(
                self.BASE_DIR, self.config['cash_filename'])

        if 'pixels' in kwargs:
            self.pixels = kwargs['pixels']
        else:
            self.pixels = pixels.Pixels(development)

        if 'playaudiofunction' in kwargs:
            self.playaudiofunction = kwargs['playaudiofunction']
        else:
            self.playaudiofunction = None

        if 'event_obj' in kwargs:
            self.event_obj = kwargs['event_obj']
        else:
            self.event_obj = threading.Event()

        if 'lock_obj' in kwargs:
            self.lock_obj = kwargs['lock_obj']
        else:
            self.lock_obj = threading.RLock()

        if 'speech_cls' in kwargs:
            self.speech = kwargs['speech_cls']
        else:
            if self.playaudiofunction is None:
                raise Exception("You must provide playaudiofunction")
            self.speech = speech.Speech(self)

        if 'speakSpeech_cls' in kwargs:
            self.speakSpeech = kwargs['speakSpeech_cls']
        else:
            self.speakSpeech = speech.SpeakSpeech(
                self.speech, self.cash_filename,
                self.pixels, sample_rate=16000)

    @property
    def api_key(self):
        return self.config['api_key']

    @property
    def catalog(self):
        return self.config['catalog']

    @property
    def host(self):
        return self.config['domen']

    @property
    def token(self):
        return self.config['token']


def ConfigGate(
        config_filename,
        inputfunction,
        reset=False,
        clean_cash=False,
        development=False):

    with open(config_filename) as f:
        config = json.load(f)
    logging.info("Loaded config with filename '%s'", config_filename)

    if reset:
        logging.info("Resetting token")
        config['token'] = None

    if inputfunction == 'rpibutton':
        logging.info("Setup input function as Button")
        inputFunc = soundProcessor.raspberryInputFunction
    elif inputfunction == 'wakeupword':
        logging.info("Setup wakeupword input finction")
        inputFunc = soundProcessor.wakeupWordInputFunction
    elif inputfunction == 'simple':
        logging.info("Setup input simple input function")
        inputFunc = soundProcessor.simpleInputFunction
    else:
        raise ValueError(
            "Invalid inputfiction '{}'. ".format(inputfunction) +
            "Avalible options: ['simple', 'rpibutton', 'wakeupword']")

    objectStorage = ObjectStorage(
        config,
        inputFunc,
        config_filename,
        development,
        playaudiofunction=speech.playaudiofunction
    )

    if clean_cash:
        logging.info("Cleanup cash")
        objectStorage.speakSpeech.reset_cash()

    return objectStorage
