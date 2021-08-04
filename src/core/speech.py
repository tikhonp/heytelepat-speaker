import logging
import os
import pickle

import requests
import simpleaudio as sa
import speech_recognition as sr
import speechkit


def play_audio_function(io_vaw, num_channels=1, bytes_per_sample=2, sample_rate=48000):
    """
    Function to play audio, that can be changed on different devices

    :param io.BytesIO io_vaw: byte array vaw audio
    :param integer num_channels: Count of channels in audio, for stereo set `2`
    :param integer bytes_per_sample: number of bytes per second (16 bit = 2 bytes)
    :param integer sample_rate: Sample rate of audio, default `48000`

    :return None:
    """
    play_obj = sa.play_buffer(
        io_vaw,
        num_channels,
        bytes_per_sample,
        sample_rate,
    )
    play_obj.wait_done()


class SynthesizedSpeech:
    def __init__(self, text, speech_cls):
        """
        Creates one sentence with method to synthesize and play

        :param string text: string text to synthesize
        :param Speech speech_cls: object of Speech class
        """
        self.synthesisSampleRateHertz = speech_cls.synthesisSampleRateHertz
        self.synthesizeAudio = speech_cls.synthesizeAudio
        self.play_audio_function = speech_cls.play_audio_function
        self.text = text
        self.audio_data = None
        self.folderId = speech_cls.objectStorage.catalog

    def synthesize(self):
        """Creates buffer io wav file that next can be played"""

        self.audio_data = self.synthesizeAudio.synthesize_stream(
            text=self.text, voice='alena', format='lpcm',
            sampleRateHertz=str(self.synthesisSampleRateHertz),
            folderId=self.folderId)

    def play(self):
        """Plays created wav with speakers"""

        logging.info("PLAYS TEXT '{}'".format(self.text))
        if self.audio_data is None:
            raise Exception(
                "Audio did not synthesized, please run \"synthesize\" first.")
        self.play_audio_function(
            self.audio_data, sample_rate=self.synthesisSampleRateHertz)


class RecognizeSpeech:
    def __init__(self, io_vaw, speech, sample_rate):
        """
        Recognizes text from given bytesio vaw

        :param io.BytesIO io_vaw: bytesio array with audio vaw
        :param Speech speech: object of Speech class
        :param integer sample_rate: Sample rate of audio
        """

        self.io_vaw = io_vaw
        self.speech = speech
        self.sample_rate = sample_rate

    def recognize(self) -> str:
        """Starting streaming to yandex api and return recognize text"""

        self.speech.pixels.think()
        logging.info("Got audio input, recognizing...")
        text = self.speech.recognizeShortAudio.recognize(
            self.io_vaw, folderId=self.speech.catalog, format='lpcm',
            sampleRateHertz=str(self.sample_rate))
        if text.strip() == '':
            text = None
        logging.info("RECOGNIZED TEXT '{}'".format(text))
        self.speech.pixels.off()
        return text


class Speech:
    """Class that realise speech recognition and synthesize methods"""

    def __init__(self,
                 object_storage,
                 timeout_speech=10,
                 phrase_time_limit=15,
                 recognizing_sample_rate_hertz=16000,
                 synthesis_sample_rate_hertz=16000):
        """
        :param ObjectStorage object_storage: ObjectStorage instance
        :param integer timeout_speech: parameter is the maximum number of seconds that this will wait for a phrase
        :param integer phrase_time_limit: parameter is the maximum seconds that this will allow a phrase to continue
        :param integer recognizing_sample_rate_hertz: sample rate for recording audio
        :param integer synthesis_sample_rate_hertz: sample rate for playing audio
        """

        self.objectStorage = object_storage
        try:
            self.synthesizeAudio = speechkit.SynthesizeAudio(
                object_storage.api_key)
            self.recognizeShortAudio = speechkit.RecognizeShortAudio(
                object_storage.api_key)
        except requests.exceptions.ConnectionError:
            logging.warning("Network is unavailable, speechkit is None")

        self.recognizingSampleRateHertz = recognizing_sample_rate_hertz
        self.synthesisSampleRateHertz = synthesis_sample_rate_hertz
        self.play_audio_function = object_storage.play_audio_function
        self.pixels = object_storage.pixels

        self.recognizer = sr.Recognizer()

        self.api_key = object_storage.api_key
        self.catalog = object_storage.catalog
        self.timeout_speech = timeout_speech
        self.phrase_time_limit = phrase_time_limit

    def init_speechkit(self):
        """If speechkit was not initialized because network down, it init"""

        self.synthesizeAudio = speechkit.SynthesizeAudio(
            self.api_key)
        self.recognizeShortAudio = speechkit.RecognizeShortAudio(
            self.api_key)

    def create_speech(self, text: str) -> SynthesizedSpeech:
        """Creates instance of SynthesizedSpeech to be used for synth later"""

        return SynthesizedSpeech(text, self)

    def read_audio(self):
        """Starting reading audio and if there is audio creates instance of RecognizeSpeech or None"""

        try:
            with sr.Microphone() as source:
                self.pixels.listen()
                data = self.recognizer.listen(
                    source,
                    timeout=self.timeout_speech,
                    phrase_time_limit=self.phrase_time_limit,
                )
                self.pixels.off()
                data_sound = data.get_raw_data(
                    convert_rate=self.recognizingSampleRateHertz)
                return RecognizeSpeech(
                    data_sound, self, self.recognizingSampleRateHertz)
        except sr.WaitTimeoutError:
            return

    def adjust_for_ambient_noise(self, duration=1):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)


class SpeakSpeech:
    """Generates plays and cashes speech generated in Speech class"""

    def __init__(self,
                 speech_cls,
                 cashed_data_filename,
                 pixels_obj):
        """
        :param Speech speech_cls: object of Speech class
        :param string cashed_data_filename: filename of pickle data
        :param pixels.Pixels pixels_obj: Object to control LEDs
        """
        self.pixels = pixels_obj
        self.speech = speech_cls
        self.cashed_data_filename = cashed_data_filename
        self.sample_rate = speech_cls.synthesisSampleRateHertz
        self.data = {}
        self.__load_data__()

    def __load_data__(self):
        try:
            with open(self.cashed_data_filename, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {}
            self.__store_data__()

    def __store_data__(self):
        logging.debug("Storing data, data: {}".format(self.data))
        os.makedirs(os.path.dirname(self.cashed_data_filename), exist_ok=True)
        with open(self.cashed_data_filename, 'wb') as f:
            pickle.dump(self.data, f)

    def reset_cash(self):
        self.data = {}
        self.__store_data__()

    def play(self, text, cache=False):
        """
        Generate and plays speech with text given

        :param string text: text to play
        :param boolean cache: if need cash it

        :return none:
        """
        self.pixels.think()
        if cache:
            if text in self.data:
                logging.debug("Cashed data found, playing it")
                synthesized_speech = self.data[text]
            else:
                logging.debug("Cashed data was not found, synthesizing, "
                              "text: '{}', keywords: '{}'".format(
                    text, self.data.keys()))
                synthesized_speech = self.speech.create_speech(text)
                synthesized_speech.synthesize()
                self.data[text] = synthesized_speech
                self.__store_data__()
        else:
            synthesized_speech = self.speech.create_speech(text)
            synthesized_speech.synthesize()

        self.pixels.speak()
        synthesized_speech.play()
        self.pixels.off()

    def cash_only(self, text: str):
        """Generate and store phrases without play it."""

        if text in self.data:
            return

        synthesized_speech = self.speech.create_speech(text)
        synthesized_speech.synthesize()
        self.data[text] = synthesized_speech
        self.__store_data__()
