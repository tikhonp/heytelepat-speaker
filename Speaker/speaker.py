#!/usr/bin/env python

from utils import main_thread, notifications_thread
import argparse
from initGates import authGate, connectionGate, configGate
import logging


logging.basicConfig(filename='myapp.log', level=logging.INFO)
logging.info("Started! OOO Telepat, all rights reserved.")


parser = argparse.ArgumentParser(description="Speaker for telepat.")
parser.add_argument('-r', '--reset', help="reset speaker token and init",
                    action='store_true')
parser.add_argument('-cc', '--cleancash', help="clean cashed speaches",
                    action='store_true')
parser.add_argument('-rb', '--rpibutton',
                    help="add input function as button pressed",
                    action='store_true')
args = parser.parse_args()

objectStorage = configGate.ConfigGate(
    config_filename='speaker_config.json',
    cash_data_filename='cash.data',
    reset=args.reset,
    rpi_button=args.rpibutton,
    clean_cash=args.cleancash
)

connectionGate.ConnectionGate(objectStorage)

objectStorage = authGate.AuthGate(objectStorage)

print("Creating notification thread...")
notifications_thread_cls = notifications_thread.NotificationsAgentThread(
    objectStorage,
    notifications_thread.notifications_list,
)

print("Creating main thread...")
main_thread_cls = main_thread.MainThread(
    objectStorage,
    main_thread.activitiesList
)

print("Running Notification thread")
notifications_thread_cls.start()

print("Running main thread")
main_thread_cls.start()
