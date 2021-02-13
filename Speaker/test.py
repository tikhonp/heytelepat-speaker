from speechkit import speechkit
from sys import argv
from datetime import datetime


script, filename, baketname = argv

objstrname = 'output' + str(str(str(datetime.now()).split(sep=' ')[1]).split(sep='.')[1]) + '.opus'
if speechkit.recode(filename, objstrname)!=0:
    raise Exception('RecoderingError')

apiKey = "AgAAAAAsHJhgAATuwZCvoKKoLUKfrwvw8kgAFv8"

recognizeShortAudio = speechkit.recognizeShortAudio(apiKey)
print(recognizeShortAudio.token)
output = recognizeShortAudio.recognize(objstrname, baketname)

print(output)
