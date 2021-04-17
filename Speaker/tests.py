import unittest
from utils import speech
import io


class TestPlayaudiofunctions(unittest.TestCase):
    def check_playaudiofuction(self):
        with open("tests_data/test_audio.wav", "rb") as f:
            print(f)
            self.assertEqual(
                speech.playaudiofunction(f.read(), sample_rate=88200),
                1
            )


class TestSynthesizeSpeech(unittest.TestCase):
    def setUp(self):
        self.speech = speech.Speech(
            "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8",
            "b1gedt47d0j9tltvtjaq",
            speech.playaudiofunction,
        )

    def test_create_SynthesizeSpeech_instance(self):
        synthesizedSpeech = self.speech.create_speech(
            "Тестирование синтеза речи!")
        self.assertIsInstance(
            synthesizedSpeech,
            speech.SynthesizedSpeech,
            msg="Create speech must return SynthesizedSpeech instance"
        )
        print(type(synthesizedSpeech.audio_data))
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()


class TestSpeechRecognition(unittest.TestCase):
    def setUp(self):
        self.speech = speech.Speech(
            "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8",
            "b1gedt47d0j9tltvtjaq",
            speech.playaudiofunction,
        )

    def test_adjustVolume(self):
        self.speech.adjust_for_ambient_noise()

    def test_recognizeText(self):
        print("Скажите, \"привет\"")
        recognizeSpeech = self.speech.read_audio()
        self.assertIsInstance(
            recognizeSpeech,
            speech.RecognizeSpeech,
            msg="Read audio must return RecognizeSpeech instance",
        )
        text = recognizeSpeech.recognize()
        self.assertEqual(
            text.lower(),
            "привет",
            msg="Убедитесь, что вы правильно произнесли \"привет\", в противном случае проверьте распознавание"
        )

    def test_silence(self):
        print("Не говорите ничего")
        recognizeSpeech = self.speech.read_audio()
        self.assertEqual(
            recognizeSpeech,
            None,
            msg="Silence must be None",
        )


if __name__ == '__main__':
    unittest.main()
