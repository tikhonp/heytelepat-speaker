def send_message(token):
    speak("Какое сообщение вы хотите отправить?")

    with sr.Microphone() as source:
        data = recognizer.listen(source)
        data_sound = data.get_raw_data(convert_rate=48000)
        recognize_text = recognizeShortAudio.recognize(data_sound, catalog)
    print(recognize_text)

    answer = requests.post(config['domen']+"/speakerapi/sendmessage/", data=json.dumps({
        'token': token,
        'message': recognize_text,
    }))
    print(answer, answer.text)

