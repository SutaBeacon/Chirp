from multiprocessing import Process, Queue, Event
from queue import Empty
import json

# from ConsoleLog import normal
from InteractionQueue import InteractionQueue


class InteractionControllerBase (Process):

    _messages = Queue()
    _handlers = {}
    commands = Queue()
    _term = Event()

    def __init__(self):
        super(InteractionControllerBase, self).__init__(target=self._mainloop)

    def message(self, msg):
        self._messages.put(msg)

    def send(self, dest, msg):
        cmd = {
            "dest": dest,
            "content": json.dumps(msg)
        }
        self.commands.put(cmd)

    def registerHandler(self, src, handler):
        self._handlers[src] = handler

    def _checkMessages(self):
        # handle messages sent to me
        while True:
            try:
                msg = self._messages.get(False)
                self._handlers[msg['src']](msg)
                self._interactions.notify(msg)
            except Empty:
                break

        # handle messages sent by interactions to be relayed
        while True:
            try:
                cmd = self._interactions.commands.get(False)
                self.commands.put(cmd)
            except Empty:
                break

    def _mainloop(self):
        self._term.clear()
        self._interactions = InteractionQueue()
        self._interactions.start()
        self.setup()
        while not self._term.is_set():
            self._checkMessages()
            self.loop()
        self.onExit()

    def terminate(self):
        self._term.set()

    def onExit(self):
        pass
