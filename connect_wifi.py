#!/usr/bin/env python3

"""
`connect_wifi.py`
Generate audio tonal code for wifi connecting
OOO Telepat, All Rights Reserved
"""

__version__ = '0.0.1'
__author__ = 'Tikhon Petrishchev'
__credits__ = 'TelePat LLC'

import argparse
import getpass
import json
import sys

import ggwave
import pyaudio

parser = argparse.ArgumentParser(description="Утилита активации колонки Telepat Medsenger.")
parser.add_argument(
    '--txProtocolId', default='2', type=int,
    help="Протокол ggwave. Default - `2`"
)
parser.add_argument(
    '--volume', default='20', type=int,
    help="Громкость ggwave. Default - `20`"
)
parser.add_argument(
    '--ssid', help='Wi-fi SSID (Имя сети).'
)
parser.add_argument(
    '--psk', help='Пароль от сети Wi-Fi.'
)
args = parser.parse_args()

print("Утилита активации колонки Telepat Medsenger.")
data = json.dumps({
    'ssid': args.ssid if args.ssid else input("Имя сети: "),
    'psk': args.psk if args.psk else getpass.getpass("Пароль: "),
})

waveform = ggwave.encode(data, txProtocolId=args.txProtocolId, volume=args.volume)

while True:
    p = None
    try:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32, channels=1, rate=48000,
            output=True, frames_per_buffer=4096)
        print("Воспроизводится аудио код... ", end='', flush=True)
        stream.write(waveform, len(waveform) // 4)
        stream.stop_stream()
        print("Готово.")
        stream.close()
    finally:
        if p:
            p.terminate()

    while True:
        s = input("Хотите воспроизвести еще раз [Y/n]? ").strip()
        if s == 'n':
            sys.exit()
        elif s == 'Y':
            break
        else:
            print("Нераспознаная операция `{}`, доступно `Y` или `n`.".format(s))
