#!/usr/bin/env python

import logging
import argparse

parser = argparse.ArgumentParser(description="Speaker for telepat.")
parser.add_argument('-r', '--reset', help="reset speaker token and init",
                    action='store_true')
parser.add_argument('-cc', '--cleancash', help="clean cashed speaches",
                    action='store_true')
parser.add_argument('-d', '--development',
                    help="Develoment mode, can't be used with button",
                    action='store_true')
parser.add_argument('-s', '--store_cash',
                    help="Store cash sound for network connection",
                    action='store_true')
parser.add_argument(
    '-infunc', '--inputfunction', default='simple',
    help=(
        "Provide input function. "
        "Options: ['simple', 'rpibutton', 'wakeupword'] "
        "Example: -infunc=rpibutton, default='simple'"
    )
)
parser.add_argument(
    '-log',
    '--loglevel',
    default='warning',
    help=(
        "Provide logging level. "
        "Example -log=debug, default='warning'"
    ),
)
args = parser.parse_args()

numeric_level = getattr(logging, args.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.loglevel)

logging.basicConfig(
    # filename='/home/pi/heytelepat/Speaker/sp.log',
    format='%(asctime)s - %(levelname)s - '
           '[%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=numeric_level
)

logging.info("Started! OOO Telepat, all rights reserved.")

from initGates import authGate, connectionGate, configGate
from dialogs import dialog, dialogList
from soundProcessor import SoundProcessor
from events import event, eventsList
import systemd.daemon


if not args.development:
    import alsaaudio

    m = alsaaudio.Mixer(control='Speaker', cardindex=1)
    m.setvolume(90)
else:
    logging.warning("AlsaAudio is not used, development mode")

if args.development and args.inputfunction == 'rpibutton':
    raise Exception("Rpi Button can't be used with development mode")

objectStorage = configGate.ConfigGate(
    config_filename='speaker_config.json',
    inputfunction=args.inputfunction,
    reset=args.reset,
    clean_cash=args.cleancash,
    development=args.development,
)

connectionGate.ConnectionGate(objectStorage)

if args.store_cash:
    logging.info("Store cash active")
    connectionGate.cash_phrases(objectStorage.speakSpeech)

objectStorage = authGate.AuthGate(objectStorage)

dialogEngineInstance = dialog.DialogEngine(
                        objectStorage,
                        dialogList.dialogs_list)

soundProcessorInstance = SoundProcessor(objectStorage, dialogEngineInstance)

eventsEngineInstance = event.EventsEngine(
    objectStorage,
    eventsList.events_list,
    dialogEngineInstance
)
eventsEngineInstance.start()

soundProcessorInstance.start()

systemd.daemon.notify('READY=1')
