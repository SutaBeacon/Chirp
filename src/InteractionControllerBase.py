from multiprocessing import Process, Queue, Event
from queue import Empty
import json

# from ConsoleLog import normal
from InteractionQueue import InteractionQueue


class InteractionControllerBase ():

    _messages = Queue()
    _handlers = {}
    commands = Queue()
    _term = Event()

    def __init__(self):
        self._term.clear()
        self._interactions = InteractionQueue()
        self._interactions.start()
        self.setup()

    def message(self, msg):
        self._handlers[msg['src']](msg)
        self._interactions.notify(msg)

    def send(self, dest, msg):
        cmd = {
            "dest": dest,
            "content": json.dumps(msg)
        }
        self.commands.put(cmd)

    def registerHandler(self, src, handler):
        self._handlers[src] = handler

    def _checkMessages(self):
        while True:
            try:
                cmd = self._interactions.commands.get(False)
                self.commands.put(cmd)
            except Empty:
                break

    def mainloop(self):
        self._checkMessages()
        self.loop()

    def terminate(self):
        self._term.set()

    def onExit(self):
        pass
