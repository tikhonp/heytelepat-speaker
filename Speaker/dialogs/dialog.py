import logging
from collections import deque


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

    def _execute_next_dialog(self):
        if self.currentDialog is None and self.dialogQueue:
            logging.debug("Trying to get dialog from queue")
            self.currentDialog = self.dialogQueue.popleft()
            logging.debug("Got dialog from queue")

            with self.objectStorage.lock_obj:
                self.currentDialog.process_input()

    def add_dialog_to_queue(self, dialog):
        if self.currentDialog is None:
            self.currentDialog = dialog
            self.process_input(None)
        else:
            logging.debug("Putting dialog {} into queue".format(dialog))
            self.dialogQueue.append(dialog)
            logging.debug("Puted dialog {} into queue".format(dialog))
            self._execute_next_dialog()

    def process_input(self, text: str):
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
        elif self.currentDialog.need_permanent_answer:
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
