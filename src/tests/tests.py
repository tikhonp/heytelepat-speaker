import unittest

from core import speech


class TestPlayAudioFunctions(unittest.TestCase):
    def check_play_audio_function(self):
        with open("test_audio.wav", "rb") as f:
            print(f)
            self.assertEqual(
                speech.play_audio_function(f.read(), sample_rate=88200),
                1
            )


class TestSynthesizeSpeech(unittest.TestCase):
    # def setUp(self):
    #     self.speech = speech.Speech(
    #         "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8",
    #         "b1gedt47d0j9tltvtjaq",
    #         speech.play_audio_function,
    #     )

    def test_create_SynthesizeSpeech_instance(self):
        synthesized_speech = self.speech.create_speech(
            "Тестирование синтеза речи!")
        self.assertIsInstance(
            synthesized_speech,
            speech.SynthesizedSpeech,
            msg="Create speech must return SynthesizedSpeech instance"
        )
        synthesized_speech.synthesize()
        synthesized_speech.play()


class TestSpeechRecognition(unittest.TestCase):
    # def setUp(self):
    #     self.speech = speech.Speech(
    #         "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8",
    #         "b1gedt47d0j9tltvtjaq",
    #         speech.play_audio_function,
    #     )

    def test_adjustVolume(self):
        self.speech.adjust_for_ambient_noise()

    def test_recognizeText(self):
        print("Скажите, \"привет\"")
        recognize_speech = self.speech.read_audio()
        self.assertIsInstance(
            recognize_speech,
            speech.RecognizeSpeech,
            msg="Read audio must return RecognizeSpeech instance",
        )
        text = recognize_speech.recognize()
        self.assertEqual(
            text.lower(),
            "привет",
            msg="Убедитесь, что вы правильно произнесли \"привет\", в противном случае проверьте распознавание"
        )

    def test_silence(self):
        print("Не говорите ничего")
        recognize_speech = self.speech.read_audio()
        self.assertEqual(
            recognize_speech,
            None,
            msg="Silence must be None",
        )


if __name__ == '__main__':
    unittest.main()
