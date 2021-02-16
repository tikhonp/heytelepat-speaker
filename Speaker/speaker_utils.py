from pydub import AudioSegment
from speechkit import speechkit
import speech_recognition as sr
from playsound import playsound


class Speech:
    def __init__(self, config):
        self.filename = config['filename']
        self.filenamev = config['filenamev']

        self.synthesizeAudio = speechkit.synthesizeAudio(
            config['apiKey'], config['catalog'])
        self.recognizeShortAudio = speechkit.recognizeShortAudio(
            config['apiKey'])
        self.recognizer = sr.Recognizer()

        # self.scheduler = sched.scheduler(time.time, time.sleep)

    def speak(self, text):
        self.synthesizeAudio.synthesize(text, self.filename)

        AudioSegment.from_file(self.filename).export(
            self.filenamev, format="wav")
        speechkit.removefile(self.filename)

        playsound(self.filenamev)
        speechkit.removefile(self.filenamev)
