from threading import Thread
import logging
try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("RPi.GPIO is not available, button is disabled")


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
                    "Я не расслышал, повторите, пожалуйста еще.", cashed=True)
                return

            text = recognizeSpeech.recognize()
            if text is None:
                self.objectStorage.speakSpeech.play(
                    "Я не расслышал, повторите, пожалуйста еще.", cashed=True)
                return

            return text

    def _run_item(self):
        # process sound input

        self.objectStorage.inputFunction()

        text = self._get_voice_sr()
        if text is not None:
            self.dialogEngineInstance.process_input(text)

    def run(self):
        logging.info("Started soundProcessorInstance")
        while True:
            # try:
            self._run_item()
            # except Exception as e:
                # logging.error("There is error in sound_processor: %s", e)
