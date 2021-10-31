#!/usr/bin/env python

"""
`speaker.py`
Input point for Telepat Speaker
OOO Telepat, All Rights Reserved
"""

__version__ = '0.5.2'
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
    format='%(asctime)s - %(levelname)s - '
           '[%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=numeric_level
)

logging.info("Started! OOO Telepat, all rights reserved. [{}]".format(__version__))

try:
    from init_gates import auth_gate, connection_gate, config_gate
    from init_gates.connection_gate import cash_phrases, BasePhrases
    from dialogs import DialogEngine, dialogs_list
    from events import EventsEngine, events_list
    from core import SoundProcessor
except ImportError as e:
    logging.error("Error with importing modules {}".format(e))
    raise e

if args.systemd:
    from cysystemd.daemon import notify, Notification

if args.development and args.input_function == 'rpi_button':
    logging.error("Rpi Button can't be used with development mode")
    sys.exit()

objectStorage = config_gate(
    input_function=args.input_function,
    debug_mode=True if args.loglevel.lower() == 'debug' else False,
    reset=args.reset,
    clean_cash=args.clean_cash,
    development=args.development,
    version=__version__,
)

if args.store_cash:
    logging.info("Store cash active")
    cash_phrases(objectStorage.play_speech)
    sys.exit()

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

if objectStorage.token is None:
    objectStorage.play_speech.play(BasePhrases.hello, cache=True)

if args.systemd:
    notify(Notification.READY)
    notify(Notification.STATUS, "Connection Gate...")

objectStorage.auth_code = connection_gate(objectStorage)

if args.systemd:
    notify(Notification.STATUS, "Auth Gate...")

objectStorage = auth_gate(objectStorage)

dialogEngineInstance = DialogEngine(objectStorage, dialogs_list)

if args.systemd:
    notify(Notification.STATUS, "Loading main processes...")


async def main():
    sound_processor_instance = SoundProcessor(objectStorage, dialogEngineInstance)

    events_engine_instance = EventsEngine(objectStorage, events_list, dialogEngineInstance)

    sound_processor_task = objectStorage.event_loop.create_task(sound_processor_instance.run())
    events_engine_task = objectStorage.event_loop.create_task(events_engine_instance.run())

    if args.systemd:
        notify(Notification.STATUS, "Loaded all processes, running...")

    objectStorage.pixels.wakeup()
    return (sound_processor_task, events_engine_task), (sound_processor_instance, events_engine_instance)


async def shutdown(tasks_to_stop: list, objects_to_kill: list) -> None:
    objectStorage.pixels.off()
    for obj in objects_to_kill:
        await obj.kill()
    await asyncio.gather(*tasks_to_stop)

    # pending = asyncio.Task.all_tasks()
    # for task in pending:
    #     await task.kill()
    # await asyncio.gather(*pending)


tasks, objects = objectStorage.event_loop.run_until_complete(main())
logging.info("Loaded all processes, running...")

if not args.development:
    objectStorage.play_speech.play("Я готов. Для того, чтобы задать вопрос нажмите на кнопку.")

try:
    objectStorage.event_loop.run_until_complete(asyncio.gather(*tasks))
except KeyboardInterrupt:
    logging.info("Stopping...")
finally:
    objectStorage.event_loop.run_until_complete(shutdown(tasks, objects))
    objectStorage.event_loop.close()
    sys.exit()
