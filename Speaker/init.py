from network import network
import ggwave
import pyaudio
import json


def get_ggwave_input():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paFloat32, channels=1,
                    rate=48000, input=True, frames_per_buffer=1024)

    instance = ggwave.init()

    while True:
        data = stream.read(1024, exception_on_overflow=False)
        res = ggwave.decode(instance, data)
        if (not res is None):
            try:
                data_str = res.decode('utf-8')
                return data_str
            except:
                pass

    ggwave.free(instance)

    stream.stop_stream()
    stream.close()

    p.terminate()

def wirless_network_init():
    # say about lisening code
    data = get_ggwave_input()
    data = json.loads(data)

    n = network.Network(data['ssid'])
    if not n.check_available():
        # say about not availible
        print("Not availible")

    n.create(data['psk'])
    if not n.connect():
        # say about connection error
        print("Connection error")

def first_init():
    if not network.check_connection_hardware() or \
            not network.check_really_connection():
        wireless_network_init()

wirless_network_init()
