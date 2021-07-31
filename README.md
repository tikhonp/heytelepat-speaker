# heytelepat
Hey Telepat - project with voice assistant for teleport messenger integration

> Warning! `python3.8` or grater required!

# Getting started
Raspberry Pi full installation ([Seeedstudio ReSpeaker 2-Mics Pi HAT](https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/) required):

```bash
$ git clone https://github.com/TikhonP/heytelepat-speaker.git
$ cd heytelepat-speaker/installation
$ ./install.sh
```

Then reboot.

Init settings can be configured in `src/settings.ini`

## Usage

Control main program with `systemd`:

Start: `sudo systemctl start speaker`

Stop: `sudo systemctl stop speaker`

Restart `sudo systemctl restart speaker`

Check status and logs:

Status: `sudo status stop speaker`

Log: `sudo journalctl -f -u speaker`

Updater service called `speaker_updater.service` and can be controlled similar to `speaker.service`.
It loads every hour with `speaker_updater.timer`.

# Demo Speaker macOS install

Python 3 and python virtual environment required

```bash 
$ git clone https://github.com/TikhonP/heytelepat-speaker.git
$ cd heytelepat-speaker
$ python3 -m venv env
$ . env/bin/activate
$ pip install -r installation/requirements_macos.txt
```
Then just run:

```bash
$ cd src
$ ./speaker.py -d
```

You can set options, just type help:

```
$ ./speaker.py -h
usage: speaker.py [-h] [-r] [-cc] [-d] [-s] [-symd] [-in_func INPUT_FUNCTION] [-log LOGLEVEL]

Speaker for telepat.

optional arguments:
  -h, --help            show this help message and exit
  -r, --reset           reset speaker token and init
  -cc, --clean_cash     clean cache speeches
  -d, --development     Development mode, can't be used with button
  -s, --store_cash      Store cash sound for network connection
  -symd, --systemd      Option for running as systemd service
  -in_func INPUT_FUNCTION, --input_function INPUT_FUNCTION
                        Provide input function. Options: ['simple', 'rpi_button', 'wake_up_word'] Example: -in_func=rpi_button, default='simple'
  -log LOGLEVEL, --loglevel LOGLEVEL
                        Provide logging level. Example -log=debug, default='warning'
```

# Packaging
Note: check that `settings.ini` version similar to `speaker.__version__`

On macOS:

```bash
$ cd heytelepat-speaker
$ tar czf firmware_<version major.minor.fix>.tar.gz src
```

# Todo

Add to install:

```bash
$ sudo apt-get install libasound2-plugins
```

# License

Copyright 2021 OOO Telepat, Tikhon Petrishchev