"""
Utils for using Yandex Speechkit with speechkit lib, listen phrases and synthesis.
"""

import os
import pickle

import pyaudio
import simpleaudio as sa
from iterators import TimeoutIterator
from speechkit import Session, SpeechSynthesis, DataStreamingRecognition

from core.speaker_logging import get_logger

logger = get_logger()

try:
    import RPi.GPIO as GPIO
except ImportError:
    logger.warning("RPi.GPIO is not available, button is disabled")


def pyaudio_play_audio_function(audio_data, num_channels=1, sample_rate=48000, chunk_size=4000):
    """
    Function to play audio, that can be changed on different devices
    :param bytes audio_data: byte array vaw audio
    :param integer num_channels: Count of channels in audio, for stereo set `2`
    :param integer sample_rate: The sampling frequency of the submitted audio, default `48000`
    :param integer chunk_size: Size of one readable chunk, default `4000`
    :rtype: None
    """
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=num_channels,
        rate=sample_rate,
        output=True,
        frames_per_buffer=chunk_size
    )

    try:
        for i in range(0, len(audio_data), chunk_size):
            stream.write(audio_data[i:i + chunk_size])
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def raspberry_simple_audio_play_audio_function(audio_data, num_channels=1, sample_rate=48000, gpio_pin=17):
    """
    Function to play audio, that can be changed on different devices

    :param bytes audio_data: byte array vaw audio
    :param integer num_channels: Count of channels in audio, for stereo set `2`
    :param integer sample_rate: The sampling frequency of the submitted audio, default `48000`
    :param integer gpio_pin: Pin which button connected to
    :rtype: None
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_UP)

    play_obj = sa.play_buffer(
        audio_data,
        num_channels,
        2,  # Number of bytes per second (16 bit = 2 bytes)
        sample_rate,
    )
    while play_obj.is_playing():
        if GPIO.input(gpio_pin) == GPIO.LOW:
            play_obj.stop()
            break


def simple_audio_play_audio_function(audio_data, num_channels=1, sample_rate=48000):
    """
    Function to play audio, that can be changed on different devices

    :param bytes audio_data: byte array vaw audio
    :param integer num_channels: Count of channels in audio, for stereo set `2`
    :param integer sample_rate: The sampling frequency of the submitted audio, default `48000`
    :rtype: None
    """
    play_obj = sa.play_buffer(
        audio_data,
        num_channels,
        2,  # Number of bytes per second (16 bit = 2 bytes)
        sample_rate,
    )
    play_obj.wait_done()


default_play_audio_function = pyaudio_play_audio_function


def gen_audio_capture_function(sample_rate, chunk_size=4000, num_channels=1):
    """
    Generates audio for using streaming recognition

    :param integer sample_rate: The sampling frequency of the submitted audio.
    :param integer chunk_size: Size of one readable chunk, default `4000`
    :param integer num_channels: Count of channels in audio, for stereo set `2`, default `1`
    :return: Yields pcm data bytes format
    :rtype: Iterator[bytes]
    """

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=num_channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size
    )
    try:
        while True:
            yield stream.read(chunk_size, exception_on_overflow=False)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


class ListenRecognizeSpeech:
    """Listen and recognize audio using speechkit."""

    def __init__(
            self, session, pixels, sample_rate=8000, timeout=15, generate_audio_function=gen_audio_capture_function
    ):
        """
        :param Session session: speechkit Session
        :param core.pixels.Pixels pixels: Object to control LEDs
        :param integer sample_rate: Sample rate of audio, default `8000`
        :param integer timeout: Timeout in seconds, default `15`
        :param function generate_audio_function: Function generates audio data
        """
        self.pixels = pixels
        self.sample_rate = sample_rate
        self.timeout = timeout
        self.generate_audio_function = generate_audio_function

        self.data_streaming_recognition = DataStreamingRecognition(
            session,
            language_code='ru-RU',
            audio_encoding='LINEAR16_PCM',
            sample_rate_hertz=sample_rate,
            partial_results=False,
            single_utterance=True,
        )

    def listen(self):
        """
        Listen phrase and recognizes text from audio stream

        :return: Recognized Text or None if timeout or empty string
        :rtype: str | None
        """
        self.pixels.listen()
        logger.info("Listening audio input, recognizing...")

        for text, final, _ in TimeoutIterator(
                self.data_streaming_recognition.recognize(self.generate_audio_function, self.sample_rate),
                timeout=self.timeout, sentinel=([None], True, False)
        ):
            text = text[0]
            if text and text.strip() == '':
                text = None

            logger.info("RECOGNIZED TEXT '{}'".format(text))
            self.pixels.off()
            return text


class PlaySpeech:
    """Generates plays and cashes speech"""
    voice = 'filipp'  # 'alena'
    speed = 1.15

    def __init__(
            self,
            session,
            cashed_data_filename,
            pixels,
            play_audio_function=default_play_audio_function,
            sample_rate_hertz=16000,
    ):
        """
        :param Session session: speechkit Session
        :param string cashed_data_filename: filename of pickle data
        :param core.pixels.Pixels pixels: Object to control LEDs
        :param function play_audio_function: Function that plays raw audio bytes
        :param integer synthesis_sample_rate_hertz: sample rate for playing audio, default `16000`
        """
        self.pixels = pixels
        self.cashed_data_filename = cashed_data_filename
        self.sample_rate = sample_rate_hertz
        self.play_audio_function = play_audio_function

        self.speech_synthesis = SpeechSynthesis(session) if session else None
        self.data = {}
        self._load_data()

    def _load_data(self):
        """Load data from file, and store it into `self.data`."""

        try:
            with open(self.cashed_data_filename, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {}
            self._store_data()

    def _store_data(self):
        """Store data to file or create it if file does not exists."""

        logger.debug("Storing data, data: {data_keys}".format(data_keys=self.data.keys()))
        os.makedirs(os.path.dirname(self.cashed_data_filename), exist_ok=True)
        with open(self.cashed_data_filename, 'wb') as f:
            pickle.dump(self.data, f)

    def _synthesize_data(self, text):
        """
        Synthesis bytes from given text

        :param string text: Text to synthesize
        :return: Bytes audio data
        :rtype: bytes
        """
        return self.speech_synthesis.synthesize_stream(
            text=text, voice=self.voice, format='lpcm', sampleRateHertz=str(self.sample_rate), speed=self.speed
        )

    def reset_cash(self):
        """Clear all data stored in file."""

        self.data = {}
        self._store_data()

    def play(self, text, cache=False):
        """
        Generate and plays speech with text given

        :param string text: Text to play
        :param boolean cache: If need cash it
        :rtype: None
        """
        self.pixels.think()
        if cache:
            if text in self.data:
                logger.debug("Cashed data found, playing it")
                audio_data = self.data[text]
            else:
                logger.debug("Cashed data was not found, synthesizing, "
                             "text: '{text}', keywords: '{data_keys}'".format(text=text, data_keys=self.data.keys()))
                audio_data = self.cash_only(text)
        else:
            audio_data = self._synthesize_data(text)

        logger.info("PLAYS TEXT '{}'".format(text))
        self.pixels.speak()
        self.play_audio_function(audio_data, sample_rate=self.sample_rate)
        self.pixels.off()

    def cash_only(self, text):
        """
        Generate and store phrases without play it.

        :param string text: Text to synthesize
        :return: Bytes audio data
        :rtype: bytes
        """
        if not isinstance(text, str):
            raise ValueError("`text` must be str, but got {}".format(type(text)))

        if text in self.data:
            return

        audio_data = self._synthesize_data(text)
        self.data[text] = audio_data
        self._store_data()
        return audio_data
