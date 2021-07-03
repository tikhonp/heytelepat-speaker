from speechkit import speechkit
import speech_recognition as sr
import simpleaudio as sa
import pickle
from utils import pixels
import logging
import requests


def playaudiofunction(
        io_vaw,
        num_channels=1,
        bytes_per_sample=2,
        sample_rate=44100):
    """
    Function to play audio, that can be changed on different devices
    : param io_vaw: byte array vaw audio
    """
    play_obj = sa.play_buffer(
        io_vaw,
        num_channels,
        bytes_per_sample,
        sample_rate,
    )
    play_obj.wait_done()
    return 1


class SynthesizedSpeech:
    def __init__(self, text, speech_cls):
        """
        Creates one sentence with method to syntethize and play
        : param text: string text to syntheze
        : param speech: object of Speech class
        """
        self.synthesisSampleRateHertz = speech_cls.synthesisSampleRateHertz
        self.synthesizeAudio = speech_cls.synthesizeAudio
        self.playaudiofunction = speech_cls.playaudiofunction
        self.text = text
        self.audio_data = None

    def syntethize(self):
        """
        Creates buffer io wav file that next can be plaeyed
        """
        self.audio_data = self.synthesizeAudio.synthesize_stream(
                self.text, lpcm=True,
                sampleRateHertz=self.synthesisSampleRateHertz)

    def play(self):
        """
        Plays created wav with speakers
        """
        logging.info("PLAYS TEXT {}".format(self.text))
        if self.audio_data is None:
            raise Exception(
                "Audio did not synthesized, please run \"synthesize\" first.")
        self.playaudiofunction(
            self.audio_data, sample_rate=self.synthesisSampleRateHertz)


class RecognizeSpeech:
    def __init__(self, io_vaw, speech, sample_rate):
        """
        Recognizes text from given bytesio vaw
        : param io_vaw: bytesio array with audio vaw
        : param speech: object of Speech class
        """

        self.io_vaw = io_vaw
        self.speech = speech
        self.sample_rate = sample_rate

    def recognize(self):
        """
        Starting streaming to yandex api and return recognize text
        """

        self.speech.pixels.think()
        logging.info("Got audio input, recognizing...")
        text = self.speech.recognizeShortAudio.recognize(
                self.io_vaw, self.speech.catalog, self.sample_rate)
        if text.strip() == '':
            text = None
        logging.info("RECOGNIZED TEXT {}".format(text))
        self.speech.pixels.off()
        return text


class Speech:
    def __init__(self,
                 api_key,
                 catalog,
                 playaudiofunction,
                 pixels,
                 timeout_speech=10,
                 phrase_time_limit=15,
                 recognizingSampleRateHertz=16000,
                 synthesisSampleRateHertz=48000):
        """
        Class that realase speech recognition and synthesize methods
        :param api_key: string Yandex API key
        :param catalog: string Yandex catalog
        :param playaudiofunction: function to play vaw bytesio
        :param pixels: instance of Pixels() object to control leds
        :param timeout_speech: parameter is the maximum number of seconds
                                    that this will wait for a phrase
        :param phrase_time_limit: parameter is the maximum number of seconds
                                    that this will allow a phrase to continue
        """

        try:
            self.synthesizeAudio = speechkit.SynthesizeAudio(
                api_key, catalog)
            self.recognizeShortAudio = speechkit.RecognizeShortAudio(
                api_key)
        except requests.exceptions.ConnectionError:
            self.api_key = api_key
            logging.warning("Network is unavailable, speeckit is None")

        self.recognizingSampleRateHertz = recognizingSampleRateHertz
        self.synthesisSampleRateHertz = synthesisSampleRateHertz
        self.playaudiofunction = playaudiofunction
        self.pixels = pixels

        self.recognizer = sr.Recognizer()

        self.catalog = catalog
        self.timeout_speech = timeout_speech
        self.phrase_time_limit = phrase_time_limit

    def init_speechkit(self):
        """
        If speechkit was not initilized becouse network down, it inits
        """
        if self.api_key is None:
            raise Exception("speechkit already initilised")

        self.synthesizeAudio = speechkit.SynthesizeAudio(
                self.api_key, self.catalog)
        self.recognizeShortAudio = speechkit.RecognizeShortAudio(
                self.api_key)

    def create_speech(self, text: str):
        """
        Creates inctance of SynthesizedSpeech to be used for synth later
        """
        return SynthesizedSpeech(text, self)

    def read_audio(self):
        """
        Starting reading audio and if there is audio creates instance
                                                of RecognizeSpeech or None
        """
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
            return None

    def adjust_for_ambient_noise(self, duration=3):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)


class SpeakSpeech:
    """
    Generates playes and cashes speech generated in Speech class
    """
    def __init__(self,
                 speech_cls: Speech,
                 cashed_data_filename: str,
                 pixels: pixels.Pixels,
                 sample_rate=48000):
        """
        :param speech_cls: object of Speech class
        :cashed_data_filename: filename of pickle data
        """
        self.pixels = pixels
        self.speech = speech_cls
        self.cashed_data_filename = cashed_data_filename
        self.sample_rate = sample_rate
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
        with open(self.cashed_data_filename, 'wb') as f:
            pickle.dump(self.data, f)

    def reset_cash(self):
        self.data = {}
        self.__store_data__()

    def play(self, text: str, cashed=False):
        """
        Generate and plays text with text given
        :param cashed: bool if need cash it
        """
        if cashed:
            if text in self.data:
                synthesizedSpeech = self.data[text]
            else:
                synthesizedSpeech = self.speech.create_speech(text)
                synthesizedSpeech.syntethize()
                self.data[text] = synthesizedSpeech
                self.__store_data__()
        else:
            synthesizedSpeech = self.speech.create_speech(text)
            synthesizedSpeech.syntethize()

        self.pixels.speak()
        synthesizedSpeech.play()
        self.pixels.off()

    def cash_only(self, text: str):
        """
        Generate and store phrases without play it
        """
        if text in self.data:
            return

        synthesizedSpeech = self.speech.create_speech(text)
        synthesizedSpeech.syntethize()
        self.data[text] = synthesizedSpeech
        self.__store_data__()
