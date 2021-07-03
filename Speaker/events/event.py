from threading import Thread
from dialogs.dialog import Dialog
import logging


class EventDialog(Thread, Dialog):
    event_happend = False
    running = False

    def __init__(self, objectStorage):
        Thread.__init__(self)
        Dialog.__init__(self, objectStorage)

        logging.debug("Creating EventDialog '{}'".format(self.name))

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        while not self.event_happend:
            self._loop_item()
            self.objectStorage.event_obj.wait(5)


class EventsEngine(Thread):
    def __init__(self, objectStorage, eventsDialogList, dialogEngineInstance):
        super().__init__()
        self.objectStorage = objectStorage
        self.eventsDialogList = eventsDialogList
        self.runningEvents = []
        self.dialogEngineInstance = dialogEngineInstance
        logging.info("Creating events engine Thread")

    def _first_run(self):
        for event in self.eventsDialogList:
            e = event(self.objectStorage)
            e.start()
            self.runningEvents.append(e)

    def run(self):
        logging.info("Starting events engine Thread")

        self._first_run()

        while True:
            create_new_indx = []
            for i, event in enumerate(self.runningEvents):
                if event.event_happend:
                    if not event.running:
                        event.running = True
                        self.dialogEngineInstance.add_dialog_to_queue(event)
                    elif event.is_done:
                        create_new_indx.append(i)

            for i in create_new_indx:
                event = self.runningEvents.pop(i)
                new_event = event.__class__(self.objectStorage)
                new_event.start()
                self.runningEvents.append(new_event)
