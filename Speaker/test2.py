from speechkit import speechkit
from sys import argv
from pydub import AudioSegment
from playsound import playsound


apiKey = "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8"
catalog = "b1gedt47d0j9tltvtjaq"

filename =  "./speech.ogg"

synthesizeAudio = speechkit.synthesizeAudio(apiKey, catalog)
synthesizeAudio.synthesize(argv[1], filename)

AudioSegment.from_file(filename).export(filename.replace(".ogg", ".wav"), format="wav")
speechkit.removefile(filename)

filename = filename.replace(".ogg", ".wav")

def signal(trek):
    """ функция включения звукового сигнала
    :param: trek (wav)
    """
    wave_obj = sa.WaveObject.from_wave_file(trek)
    play_obj = wave_obj.play()
    play_obj.wait_done()

playsound(filename)
print("done")
speechkit.removefile(filename)

