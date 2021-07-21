import logging
from collections import deque
import time
import requests


class Dialog:
    """Base class to build dialogs

    Attributes:
        cur (function)               Stores function to execute next, if `None` dialog stops
        name (string)                Name for logging
        keywords (list[str])         List of strings that are keywords to start dialog by keyword
        need_permanent_answer (bool) If true sound processor listen will permanently activate after one dialog func
        stop_words (list[str])       List of strings with stop words for dialog
    """

    cur = None
    name = 'default'
    keywords = []
    need_permanent_answer = False
    stop_words = ['хватит']

    def __init__(self, object_storage):
        """
        :param ObjectStorage object_storage: ObjectStorage instance
        """
        if not isinstance(self.name, str):
            raise TypeError("Name must be string")
        if not isinstance(self.keywords, list):
            raise TypeError("Keywords must be a list")
        if not isinstance(self.stop_words, list):
            raise TypeError("stop_words must be a list")
        self.stop_words = [i.lower() for i in self.stop_words]

        self.objectStorage = object_storage

    def _process_input(self, input_str: str):
        """Processes input text with current dialog or stops dialog"""

        if not callable(self.cur):
            raise TypeError("`self.cur` must be function")

        self.need_permanent_answer = False
        if any(word in input_str.lower() for word in self.stop_words):
            self.cur = None
            return

        logging.debug(
            "Processing input in dialog {}, with input {}".format(
                self.__str__(), input_str))

        f = self.cur
        self.cur = None
        f(input_str)

    @property
    def _is_done(self):
        """Indicates if dialog empty"""

        return True if self.cur is None else False

    def __str__(self):
        return self.name

    def fetch_data(self, request_type, *args, **kwargs):
        """Represents request to server and handles errors

        :param string request_type: Must be `requests` method, like `get` or `post`
        """
        if not hasattr(requests, request_type):
            raise ValueError("`request_type` must be `requests` method, like `get` or `post`")

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
    def __init__(self, object_storage, dialogs):
        """
        :param object_storage: ObjectStorage instance
        :param dialogs: list of dialog Instances
        """
        logging.info("Creating DialogEngine, with %d dialogs", len(dialogs))
        self.objectStorage = object_storage
        self.dialogs = dialogs
        self.dialogQueue = deque()
        self.currentDialog = None
        self.time_delay = 30
        self.cur_dialog_time = None

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
            logging.debug("Put dialog {} into queue".format(dialog))
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
            "Got text and chased dialog {}".format(self.currentDialog))
        with self.objectStorage.lock_obj:
            self.currentDialog._process_input(text)

        logging.debug("Current dialog {} is done {}".format(
            self.currentDialog, self.currentDialog._is_done))

        if self.currentDialog._is_done:
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
                        "Chased dialog {}, with keyword ".format(dialog) +
                        "'{}' in text '{}'".format(keyword, text))
                    return dialog(self.objectStorage)
