# heytelepat
Hey Telepat - project with voice assistant for teleport messenger integration

# Demo Speaker Mac OS install

Python 3 and python virtual enviroment required

```bash 
$ cd heytelepat/Speaker
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r req_macos.txt
```
And now just run:

```bash
$ ./speaker.py
```

You can set options, just type help:

```
$ ./speaker.py -h
usage: speaker.py [-h] [-r] [-cc] [-d] [-s] [-infunc INPUTFUNCTION] [-log LOGLEVEL]

Speaker for telepat.

optional arguments:
  -h, --help            show this help message and exit
  -r, --reset           reset speaker token and init
  -cc, --cleancash      clean cashed speaches
  -d, --development     Develoment mode, can't be used with button
  -s, --store_cash      Store cash sound for network connection
  -infunc INPUTFUNCTION, --inputfunction INPUTFUNCTION
                        Provide input function. Options: ['simple', 'rpibutton', 'wakeupword'] Example: -infunc=rpibutton, default='simple'
  -log LOGLEVEL, --loglevel LOGLEVEL
                        Provide logging level. Example -log=debug, default='warning'
```

# Todo 
- Инструкции и картинки на экранах подключения
- рассылка заданий и опрос их
- запрос на сброс колонки
- Сокеты для получены данных с сервера