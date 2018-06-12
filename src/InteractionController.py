from multiprocessing import Process, Queue
from queue import Empty


class InteractionController (Process):

    _messages = Queue()

    def __init__(self):
        super(InteractionController, self).__init__(target=self._mainloop)

    def message(self, msg):
        self._messages.put(msg)

    def _checkMessages(self):
        while True:
            try:
                self.onMessage(self._messages.get(False))
            except Empty:
                break

    def _mainloop(self):
        self.setup()

        while True:
            self._checkMessages()
            self.loop()

        self.onExit()

    def setup(self):
        pass

    def loop(self):
        pass

    def onmessage(self, msg):
        pass
