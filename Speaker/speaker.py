#!/usr/bin/env python

import logging
import argparse
import os.path
from pathlib import Path

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
parser.add_argument('-symd', '--systemd',
                    help="Option for running as systemd service",
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

try:
    from initGates import authGate, connectionGate, configGate
    from dialogs import dialog, dialogList
    from soundProcessor import SoundProcessor
    from events import event, eventsList
except ImportError as e:
    logging.error("Error with importing modules {}".format(e))
    raise e

if args.systemd:
    from cysystemd.daemon import notify, Notification


if not args.development:
    try:
        import alsaaudio
    except ImportError:
        raise ImportError(
            "If you using development mode please turn it on '-d', or install"
            " alsaaudio module.")

    m = alsaaudio.Mixer(control='Speaker', cardindex=1)
    m.setvolume(90)
else:
    logging.warning("AlsaAudio is not used, development mode")

if args.development and args.inputfunction == 'rpibutton':
    raise Exception("Rpi Button can't be used with development mode")


config_filename = os.path.join(
    Path(__file__).resolve().parent, 'speaker_config.json')

objectStorage = configGate.ConfigGate(
    config_filename=config_filename,
    inputfunction=args.inputfunction,
    debug_mode=True if args.loglevel.lower() == 'debug' else False,
    reset=args.reset,
    clean_cash=args.cleancash,
    development=args.development,
)

if args.systemd:
    notify(Notification.READY)
    notify(Notification.STATUS, "Connection Gate...")

connectionGate.ConnectionGate(objectStorage)

if args.store_cash:
    logging.info("Store cash active")
    connectionGate.cash_phrases(objectStorage.speakSpeech)

if args.systemd:
    notify(Notification.STATUS, "Auth Gate...")

objectStorage = authGate.AuthGate(objectStorage)

dialogEngineInstance = dialog.DialogEngine(
                        objectStorage,
                        dialogList.dialogs_list)

if args.systemd:
    notify(Notification.STATUS, "Loading main processes...")

soundProcessorInstance = SoundProcessor(objectStorage, dialogEngineInstance)

eventsEngineInstance = event.EventsEngine(
    objectStorage,
    eventsList.events_list,
    dialogEngineInstance
)
eventsEngineInstance.start()

soundProcessorInstance.start()

if args.systemd:
    notify(Notification.STATUS, "Loaded all processes, running...")
