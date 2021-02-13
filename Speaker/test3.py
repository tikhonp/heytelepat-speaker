from speechkit import speechkit
from pydub import AudioSegment
from playsound import playsound
import speech_recognition as sr
from datetime import datetime
import sched
import time
import json
import requests
import threading


with open("speaker.config", "r") as f:
    data = json.load(f)

apiKey = "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8"
catalog = "b1gedt47d0j9tltvtjaq"
filename =  "speech.ogg"
filenamev =  "speech.wav"

synthesizeAudio = speechkit.synthesizeAudio(apiKey, catalog)
recognizeShortAudio = speechkit.recognizeShortAudio(apiKey)
recognizer = sr.Recognizer()
# recognizer.dynamic_energy_threshold = True

scheduler = sched.scheduler(time.time, time.sleep)


special = None

domen = "http://tikhonsystems.ddns.net"

def speak(text):
    synthesizeAudio.synthesize(text, filename)

    AudioSegment.from_file(filename).export(filenamev, format="wav")
    speechkit.removefile(filename)

    playsound(filenamev)
    speechkit.removefile(filenamev)

def init():
    global data
    speack_t = threading.Thread(target=speak, args=(
       "Привет! Это колонка Telepat Medsenger. Я помогу тебе следить за своим здоровьем. Сейчас я скажу тебе код из 6 цифр, его надо ввести в окне подключения колонки в medsenger.  Именно так я смогу подключиться.",))
    speack_t.start()
    answer = requests.post(domen+"/speakerapi/init/")
    answer = answer.json()
    data["token"] = answer["token"]
    with open("speaker.config", "w") as f:
        f.write(json.dumps(data))

    speack_t.join()

    speak(
        "Итак, твой код: {}".format(" ".join(list(str(answer["code"])))))


def checkPreasure():
    return "please check presure!"

def sayTime():
    now = datetime.now()
    return now.strftime("%A, %-H %-M")

def pills():
    return "pills processing"

def send_message():
    speak("Какое сообщение вы хотите отправить?")

    with sr.Microphone() as source:
        data = recognizer.listen(source)
        data_sound = data.get_raw_data(convert_rate=48000)
        recognize_text = recognizeShortAudio.recognize(data_sound, catalog) # распознавание ответа

    print(recognize_text)

    answer = requests.post(domen+"/speakerapi/sendmessage/", data=json.dumps({
        'token': data['token'],
        'message': recognize_text,
    }))

motions = {
    "таблет": pills,
    "сообщение": send_message,
}


init()

while True:
    input("Press enter and tell something!")

    with sr.Microphone() as source:
        data = recognizer.listen(source)
        data_sound = data.get_raw_data(convert_rate=48000)
        recognize_text = recognizeShortAudio.recognize(data_sound, catalog) # распознавание ответа

    print(recognize_text)

    if recognize_text.lower() == "хватит": break

    for i in motions:
        if i in recognize_text.lower():
            motions[i]()


    # synthesizeAudio.synthesize(say, filename)

    # AudioSegment.from_file(filename).export(filenamev, format="wav")
    # speechkit.removefile(filename)

    # playsound(filenamev)
    # speechkit.removefile(filenamev)
