import logging
from collections import deque
import time
import requests


class Dialog:
    cur = None
    name = 'default'
    keywords = []
    need_permanent_answer = False

    def __init__(self, objectStorage):
        if not isinstance(self.name, str):
            raise TypeError("Name must be string")
        if not isinstance(self.keywords, list):
            raise TypeError("Keywords must be a list")

        self.objectStorage = objectStorage

    def process_input(self, input_str):
        self.need_permanent_answer = False

        if 'хватит' in input_str.lower():
            self.cur = None
            return

        logging.debug(
            "Processing input in dialog {}, with input {}".format(
                self.__str__(), input_str))
        f = self.cur
        self.cur = None
        f(input_str)

    @property
    def is_done(self):
        return True if self.cur is None else False

    def __str__(self):
        return self.name

    def fetch_data(self, request_type: str, *args, **kwargs):
        answer = getattr(requests, request_type)(*args, **kwargs)
        if answer.status_code == 200:
            return answer.json()
        else:
            self.objectStorage.speakSpeech.play(
                "Ошибка соединения с сетью.", cashed=True)
            logging.error(
                "Error in requests, status code: '{}', answer: '{}'".format(
                    answer.status_code, answer.text[:100]))


class DialogEngine:
    def __init__(self, objectStorage, dialogs):
        """
        :param objectStorage: ObjectStorage instance
        :param dialogs: list of dialog Instances
        """
        logging.info("Creating DialogEngine, with %d dialogs", len(dialogs))
        self.objectStorage = objectStorage
        self.dialogs = dialogs
        self.dialogQueue = deque()
        self.currentDialog = None
        self.time_delay = 30

    def _execute_next_dialog(self):
        if self.currentDialog is None and self.dialogQueue:
            logging.debug("Trying to get dialog from queue")
            self.currentDialog, text = self.dialogQueue.popleft()
            logging.debug("Got dialog from queue")
            self.cur_dialog_time = time.time()
            self.process_input(text)

    def add_dialog_to_queue(self, dialog, text=''):
        if self.currentDialog is None:
            self.cur_dialog_time = time.time()
            self.currentDialog = dialog
            self.process_input(text)
        else:
            logging.debug("Putting dialog {} into queue".format(dialog))
            self.dialogQueue.append((dialog, text))
            logging.debug("Puted dialog {} into queue".format(dialog))
            self._execute_next_dialog()

    def process_input(self, text: str):
        logging.debug("Processing input in DialogEngine")
        if self.currentDialog is not None and \
                (time.time() - self.cur_dialog_time) > self.time_delay:
            self.currentDialog = None

        if self.currentDialog is None:
            self.currentDialog = self._chose_dialog_processor(text)

        if self.currentDialog is None:
            with self.objectStorage.lock_obj:
                self.objectStorage.speakSpeech.play(
                    "К сожалению, я не знаю что ответить", cashed=True)
            return

        logging.debug(
            "Got text and chosed dialog {}".format(self.currentDialog))
        with self.objectStorage.lock_obj:
            self.currentDialog.process_input(text)

        logging.debug("Current dialog {} is done {}".format(
            self.currentDialog, self.currentDialog.is_done))

        if self.currentDialog.is_done:
            self.currentDialog = None
        else:
            self.cur_dialog_time = time.time()
            if self.currentDialog.need_permanent_answer:
                return True

        self._execute_next_dialog()

    def _chose_dialog_processor(self, text: str):
        text = text.lower()
        for dialog in self.dialogs:
            for keyword in dialog.keywords:
                if keyword in text:
                    logging.debug(
                        "Chosed dialog {}, with keyword ".format(dialog) +
                        "'{}' in text '{}'".format(keyword, text))
                    return dialog(self.objectStorage)
