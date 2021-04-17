'''
import requests
# import io
import simpleaudio as sa


url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
headers = {
    'Authorization': 'Bearer ' + "t1.9euelZrJz5COlJeRiZKLncvOx8qbzO3rnpWax5zInZHMjInKjJOblJKTmZDl8_cMPyN8-e8XOhVR_N3z90xtIHz57xc6FVH8.QJgxKIQX4VSPFn4-8t0waQOE1-PTzA0m0kbiHS9Dx9Osd0al5rLQpWKpuRuya5BlC9ZHNUkFIRrveiUINeElDA",
}

data = {
    'text': "Привет проверка синтеза",
    'lang': 'ru-RU',
    'folderId': "b1gedt47d0j9tltvtjaq",
    'voice': 'alena',
}

data['format'] = 'lpcm',
data['sampleRateHertz'] = 48000,


    print("In stream")
    with requests.post(
            url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError(
                "Invalid response received: code: %d, message: %s" % (
                    resp.status_code, resp.text))

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk


resp = requests.post(url, headers=headers, data=data, stream=True)
if resp.status_code != 200:
    raise RuntimeError(
        "Invalid response received: code: %d, message: %s" % (
            resp.status_code, resp.text))
print("Here")
resp.raw.decode_content = True

play_obj = sa.play_buffer(resp.content, 1, 2, 48000)
play_obj.wait_done()
'''

from speechkit import speechkit
synthesizeAudio = speechkit.SynthesizeAudio("AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8", "b1gedt47d0j9tltvtjaq")
data = synthesizeAudio.synthesize_stream("Привет проверка синтеза", lpcm=True)

print(data)
