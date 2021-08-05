import logging
import time
from collections import deque
import functools

import requests


class Dialog:
    """Base class to build dialogs

    Attributes:
        current_input_function (function)               Stores function to execute next, if `None` dialog stops
        name (string)                Name for logging
        keywords (list[str])         List of strings that are keywords to start dialog by keyword
        need_permanent_answer (bool) If true sound processor listen will permanently activate after one dialog func
        stop_words (list[str])       List of strings with stop words for dialog
    """

    current_input_function = None
    name = 'default'
    keywords = []
    need_permanent_answer = False
    stop_words = ['хватит', 'стоп']

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

    def process_input(self, text: str):
        """Processes input text with current dialog or stops dialog"""

        text = str(text).lower().strip()
        if not callable(self.current_input_function):
            raise TypeError("`self.current_input_function` must be function")

        self.need_permanent_answer = False
        if any(word in text.lower() for word in self.stop_words):
            self.current_input_function = None
            return

        logging.debug(
            "Processing input in dialog {}, with input {}".format(
                self.__str__(), text))

        f = self.current_input_function
        self.current_input_function = None
        f(text)

    @property
    def is_done(self):
        """Indicates if dialog empty"""

        return True if self.current_input_function is None else False

    def __str__(self):
        return self.name

    def fetch_data(self, request_type, *args, **kwargs):
        """Represents request to server and handles errors

        :param string request_type: Must be `requests` method, like `get` or `post`
        """
        if not hasattr(requests, request_type):
            raise ValueError("`request_type` must be `requests` method, like `get` or `post`")

        answer = getattr(requests, request_type)(*args, **kwargs)
        if answer.ok:
            return answer.json()
        else:
            self.objectStorage.speakSpeech.play(
                "Ошибка соединения с сетью.", cache=True)
            logging.error(
                "Error in requests, status code: '{}', answer: '{}'".format(
                    answer.status_code, answer.text[:100]))

    @staticmethod
    def to_integer(text: str) -> int:
        """Validate raw input to integer"""

        if text.isdigit():
            return int(text)

        parts = str(text).split()
        integers = [int(i) for i in parts if i.isdigit()]

        return integers[0] if integers else None

    @staticmethod
    def to_float(text):
        """Validate raw input to float

        :param string text: Text as input
        :rtype: float | None
        """

        delimiter = ' и '
        if delimiter in text:
            parts = str(text).split(delimiter)
            for i, part in enumerate(parts):
                if i == (len(parts) - 1):
                    continue

                if not (left_part := Dialog.to_integer(part.split()[-1])):
                    left_part = ''
                    for letter in range(len(part) - 1, -1, -1):
                        if letter.isdigit():
                            left_part = letter + left_part
                        else:
                            break
                    if left_part == '':
                        return
                    left_part = int(left_part)

                if not (right_part := Dialog.to_integer(parts[i + 1].split()[0])):
                    right_part = ''
                    for letter in parts[i + 1]:
                        if letter.isdigit():
                            right_part += letter
                        else:
                            break
                    if right_part == '':
                        return
                    right_part = int(right_part)

                return float('.'.join([str(left_part), str(right_part)]))

        elif integer := Dialog.to_integer(text):
            return float(integer)

    @staticmethod
    def is_positive(text: str) -> bool:
        """Check if phrase is positive"""

        positive_keywords = [
            'да', 'разумеется', 'ага', 'безусловно', 'конечно', 'несомненно', 'действительно',
            'плюс', 'так', 'точно', 'угу', 'как же', 'так', 'йес', 'легко', 'ладно', 'согласен',
            'хорошо',
        ]

        return any(word in text.lower() for word in positive_keywords)

    @staticmethod
    def is_negative(text: str) -> bool:
        """Check if phrase is negative"""

        negative_keywords = [
            'не', 'несть', 'дуд', 'дожидайся', 'избавь', 'уволь', 'ничего', 'ни', 'фигушки',
        ]

        return any(word in text.lower() for word in negative_keywords)


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
        self.time_delay = 50
        self.cur_dialog_time = None

    @functools.cached_property
    def _dialogs_keywords_list(self):
        """Generate list: [(keyword, dialog)] for dialog choosing

        :return: List with dialogs and keywords
        :rtype: list
        """

        dialogs_list = list()
        for dialog in self.dialogs:
            for keyword in dialog.keywords:
                if isinstance(keyword, str):
                    keyword = keyword.strip().lower()
                    dialogs_list.append((keyword, dialog,))
                else:
                    keyword = ' '.join(list(map(lambda x: x.strip().lower(), keyword)))
                    dialogs_list.append((keyword, dialog,))

        logging.debug("Dialog list: {}".format(dialogs_list))
        return dialogs_list

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
            self.objectStorage.speakSpeech.play("К сожалению, я не знаю что ответить", cache=True)
            return

        logging.debug("Got text and chased dialog {}".format(self.currentDialog))
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

    def _get_dialog_instance(self, dialog, keyword, text):
        """Get dialog from instance

        :param Dialog dialog: Dialog class
        :param string keyword: Keyword that matched
        :param string text: Given text
        :return: Dialog instance
        :rtype: Dialog
        """

        logging.debug(
            "Chased dialog {}, with keyword ".format(dialog) +
            "'{}' in text '{}'".format(keyword, text)
        )
        # noinspection PyCallingNonCallable
        return dialog(self.objectStorage)

    def _chose_dialog_processor(self, text):
        """Chose dialog to execute by given text

        :param string text: Text based on dialog executing
        :return: Dialog instance or None
        :rtype: Dialog | None
        """

        text = text.lower().strip()
        if text == '':
            logging.warning('Got empty text in `DialogEngine._chose_dialog_processor()`')
            return

        def k_in_text(k: str) -> bool:
            return k in text

        for keyword, dialog in self._dialogs_keywords_list:
            if ' ' in keyword:
                if all(map(k_in_text, keyword.split())):
                    return self._get_dialog_instance(dialog, keyword, text)
            elif keyword in text:
                return self._get_dialog_instance(dialog, keyword, text)
