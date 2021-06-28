import ggwave
import pyaudio
import getpass
import json

p = pyaudio.PyAudio()

print("Привет! Для активации колонки предоставьте подключение к wi-fi.")
ssid = input("Введите имя сети > ")
passwd = getpass.getpass("Введите пароль от сети: ")
data = json.dumps({
    "ssid": ssid,
    "psk": passwd,
})

waveform = ggwave.encode(data, txProtocolId=2, volume=20)

while True:
    stream = p.open(
        format=pyaudio.paFloat32, channels=1, rate=48000,
        output=True, frames_per_buffer=4096)
    stream.write(waveform, len(waveform)//4)
    stream.stop_stream()
    stream.close()

    s = input("Если хотите воспроизвети еще раз введите 'y', "
              "для завершения нажмите enter: ")
    if s == "":
        break

p.terminate()
