#!/usr/bin/env python

"""
`speaker.py`
Input point for Telepat Speaker
OOO Telepat, All Rights Reserved
"""

__version__ = '0.2.0'
__author__ = 'Tikhon Petrishchev'
__credits__ = 'TelePat LLC'

import argparse
import asyncio
import logging
import sys

parser = argparse.ArgumentParser(description="Speaker for telepat.")
parser.add_argument('-r', '--reset', help="reset speaker token and init",
                    action='store_true')
parser.add_argument('-cc', '--clean_cash', help="clean cache speeches",
                    action='store_true')
parser.add_argument('-d', '--development',
                    help="Development mode, can't be used with button",
                    action='store_true')
parser.add_argument('-s', '--store_cash',
                    help="Store cash sound for network connection",
                    action='store_true')
parser.add_argument('-symd', '--systemd',
                    help="Option for running as systemd service",
                    action='store_true')
parser.add_argument(
    '-in_func', '--input_function', default='simple',
    help=(
        "Provide input function. "
        "Options: ['simple', 'rpi_button', 'wake_up_word'] "
        "Example: -in_func=rpi_button, default='simple'"
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

logging.info("Started! OOO Telepat, all rights reserved. [{}]".format(__version__))

try:
    from init_gates import auth_gate, connection_gate, config_gate
    from dialogs import dialog, dialogList
    from core.soundProcessor import SoundProcessor
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
        logging.error(
            "If you using development mode please turn it on '-d', or install"
            " alsaaudio module.")
        sys.exit()

    m = alsaaudio.Mixer(control='Speaker', cardindex=1)
    m.setvolume(90)
else:
    logging.warning("AlsaAudio is not used, development mode")

if args.development and args.input_function == 'rpi_button':
    logging.error("Rpi Button can't be used with development mode")
    sys.exit()

objectStorage = config_gate.config_gate(
    input_function=args.input_function,
    debug_mode=True if args.loglevel.lower() == 'debug' else False,
    reset=args.reset,
    clean_cash=args.clean_cash,
    development=args.development,
    version=__version__,
)

if args.systemd:
    notify(Notification.READY)
    notify(Notification.STATUS, "Connection Gate...")

connection_gate.connection_gate(objectStorage, args.systemd)

if args.store_cash:
    logging.info("Store cash active")
    connection_gate.cash_phrases(objectStorage.speakSpeech)
    sys.exit()

if args.systemd:
    notify(Notification.STATUS, "Auth Gate...")

objectStorage = auth_gate.auth_gate(objectStorage)

dialogEngineInstance = dialog.DialogEngine(
    objectStorage,
    dialogList.dialogs_list)

if args.systemd:
    notify(Notification.STATUS, "Loading main processes...")


async def main(asyncio_loop):
    sound_processor_instance = SoundProcessor(objectStorage, dialogEngineInstance, asyncio_loop)

    events_engine_instance = event.EventsEngine(
        objectStorage,
        eventsList.events_list,
        dialogEngineInstance,
        asyncio_loop,
    )

    sound_processor_task = asyncio_loop.create_task(sound_processor_instance.run())
    events_engine_task = asyncio_loop.create_task(events_engine_instance.run())

    if args.systemd:
        notify(Notification.STATUS, "Loaded all processes, running...")

    return [(sound_processor_task, events_engine_task), (sound_processor_instance, events_engine_instance)]


async def stop(_tasks: list):
    for obj in _tasks[1]:
        await obj.kill()
    await asyncio.gather(*_tasks[0])


loop = asyncio.get_event_loop()
tasks = loop.run_until_complete(main(loop))
try:
    loop.run_until_complete(
        asyncio.gather(*tasks[0])
    )
except KeyboardInterrupt:
    logging.info("Stopping...")
finally:
    loop.run_until_complete(stop(tasks))
    loop.close()
    sys.exit()
