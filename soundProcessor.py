from threading import Thread
import pyaudio
import logging
import struct
try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("RPi.GPIO is not available, button is disabled")
try:
    import pvporcupine
except ImportError:
    logging.warning("pvporcupine is not available, required -d mode")


def wakeupWordInputFunction(k=2, sensitivity=0.6):
    keywords = [
        'alexa', 'bumblebee', 'computer', 'hey google', 'hey siri',
        'jarvis', 'picovoice', 'porcupine', 'terminator'
    ]
    keyword = keywords[k]

    porcupine = pvporcupine.create(
        keywords=[keyword], sensitivities=[sensitivity])

    pa = None
    audio_stream = None

    try:
        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

        logging.info("Listening wake up word '{}'...".format(keyword))

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                break
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        porcupine.delete()


def simpleInputFunction():
    input("Press enter and tell something!")


def raspberryInputFunction(gpio_pin=17):
    logging.info("Waiting button...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_UP)

    while True:
        if GPIO.input(gpio_pin) == GPIO.LOW:
            logging.info("Button was pushed!")
            return


class SoundProcessor(Thread):
    def __init__(self, objectStorage, dialogEngineInstance):
        super(SoundProcessor, self).__init__()
        self.objectStorage = objectStorage
        self.dialogEngineInstance = dialogEngineInstance
        logging.info("Created SoundProcessor thread")

    def _get_voice_sr(self, duration=0.1):
        with self.objectStorage.lock_obj:
            self.objectStorage.speech.adjust_for_ambient_noise(
                duration=duration)

            recognizeSpeech = self.objectStorage.speech.read_audio()

            if recognizeSpeech is None:
                self.objectStorage.speakSpeech.play(
                    "Я не расслышал, повторите, пожалуйста еще.", cache=True)
                return

            text = recognizeSpeech.recognize()
            if text is None:
                self.objectStorage.speakSpeech.play(
                    "Я не расслышал, повторите, пожалуйста еще.", cache=True)
                return

            return text

    def _run_item(self):
        # process sound input

        self.objectStorage.pixels.wakeup()
        text = self._get_voice_sr()

        if text is not None:
            if self.dialogEngineInstance.process_input(text):
                self._run_item()

    def run(self):
        logging.info("Started soundProcessorInstance")
        while True:
            try:
                self.objectStorage.inputFunction()
                self._run_item()
            except Exception as e:
                logging.error("There is error in sound_processor: %s", e)
                if self.objectStorage.debug_mode:
                    raise e
