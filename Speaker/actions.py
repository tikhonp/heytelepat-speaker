import requests
from datetime import datetime
import speech_recognition as sr


def sayTime():
    now = datetime.now()
    return now.strftime("%A, %-H %-M")


def send_message(speech, config):
    speech.speak("Какое сообщение вы хотите отправить?")

    with sr.Microphone() as source:
        data = speech.recognizer.listen(source)
        data_sound = data.get_raw_data(convert_rate=48000)
        recognize_text = speech.recognizeShortAudio.recognize(
            data_sound, config['catalog'])
    print(recognize_text)

    answer = requests.post(config['domen']+"/speakerapi/sendmessage/", json={
        'token': config['token'],
        'message': recognize_text,
    })
    if answer.status_code == 200:
        speech.speak("Сообщение успешно отправлено!")
    else:
        speech.speak("Произошла ошибка приотправлении сообщения")
        print(answer, answer.text)
