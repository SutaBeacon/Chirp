from multiprocessing import Process, Queue, Event
from queue import Empty
import json
from time import time

from ConsoleLog import error
from InteractionQueue import InteractionQueue


class InteractionControllerBase ():

    _messages = Queue()
    _handlers = {}
    commands = Queue()
    _tid = 0
    _timers = []

    def setAlarm(self, t, f):
        tid = self._tid
        self._tid += 1
        targetT = time() + t
        self._timers.append([tid, targetT])
        self.registerHandler("timer" + str(tid), f)
        return tid

    def _checkTimers(self):
        for timer in self._timers:
            if time() >= timer[1]:
                self.triggerEvent("timer" + str(timer[0]), time())
                self.deleteHandlers("timer" + str(timer[0]))

    def triggerEvent(self, event, *args):
        if event in self._handlers:
            for callback in self._handlers[event]:
                callback(*args)

    def deleteHandlers(self, event):
        if event in self._handlers:
            del self._handlers[event]

    def deleteHandler(self, event, handler):
        if event in self._handlers:
            try:
                self._handlers[event].remove(handler)
            except ValueError:
                error("Handler does not exist:", handler)

    def __init__(self):
        self.interactionQueue = InteractionQueue()
        self.setup()

    def message(self, msg):
        if msg['src'] in self._handlers:
            for handler in self._handlers[msg['src']]:
                handler(msg)
        self.interactionQueue.notify(msg)

    def send(self, dest, msg):
        msg['dest'] = dest
        self.commands.put(msg)

    def registerHandler(self, src, handler):
        if src not in self._handlers:
            self._handlers[src] = []
        self._handlers[src].append(handler)

    def _checkMessages(self):
        while True:
            try:
                cmd = self.interactionQueue.commands.get(False)
                self.commands.put(cmd)
            except Empty:
                break

    def mainloop(self):
        self._checkTimers()
        self._checkMessages()
        self.interactionQueue.update()
        self.loop()

    def terminate(self):
        self.commands.close()
        self._messages.close()
        self.interactionQueue.clear()
        self.interactionQueue.terminate()

    def onExit(self):
        pass

    def setup(self):
        pass

    def loop(self):
        pass
