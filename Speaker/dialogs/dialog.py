import queue
import logging


class Dialog:
    cur = None
    name = 'default'

    def __init__(self, objectStorage):
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
        return False if self.cur is None else True

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
        self.dialogQueue = queue.Queue()
        self.currentDialog = None

    def add_dialog_to_queue(self, dialog):
        if self.currentDialog is None:
            self.currentDialog = dialog
            with self.objectStorage.lock_obj:
                self.currentDialog.process_input(None)
        else:
            self.dialogQueue.put(dialog)

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
        self.currentDialog.process_input('')

        if self.currentDialog.is_done:
            try:
                self.currentDialog = self.dialogQueue.get()
                with self.objectStorage.lock_obj:
                    self.currentDialog.process_input()
            except queue.Queue.Empty:
                self.currentDialog = None

    def _chose_dialog_processor(self, text: str):
        text = text.lower()
        for d in self.dialogs:
            for ph in d[0]:
                if ph in text:
                    return d[1](self.objectStorage)
