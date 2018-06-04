from multiprocessing import Process, Event, Queue
from queue import Empty
from time import sleep, time


class SafeProcess (Process):

    _term = Event()

    _timers = []
    _callbacks = {}
    _messages = Queue()

    _tid = 0

    def __init__(self):
        super(SafeProcess, self).__init__(target=self._mainloop)
        self._term.clear()

    def _mainloop(self):
        self.setup()

        while True:
            self._checkTimers()
            self._checkMessages()
            if self._term.is_set():
                break
            self.loop()

        self.onExit()

    def setAlarm(self, t, f):
        tid = self._tid
        self._tid += 1
        targetT = time() + t
        self._timers.append([tid, targetT])
        self._addCallback("timer" + str(tid), f)
        return tid

    def _checkTimers(self):
        for i, timer in enumerate(self._timers):
            if time() >= timer[1]:
                self._triggerEvent("timer" + str(timer[0]), time())
                self._deleteEvent("timer" + str(timer[0]))

    def _checkMessages(self):
        while True:
            try:
                self.onMessage(self._messages.get(False))
            except Empty:
                break

    def _triggerEvent(self, event, *args):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                callback(*args)

    def _addCallback(self, event, callback):
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def _deleteEvent(self, event):
        if event in self._callbacks:
            del self._callbacks[event]

    def terminate(self):
        self._term.set()

    def message(self, msg):
        self._messages.put(msg)

    def event(self, event, *args):
        self._triggerEvent(event, *args)

    def delay(self, t):
        targetTime = time() + t
        while time() < targetTime:
            pass

    def setup(self):
        pass

    def loop(self):
        pass

    def onExit(self):
        pass

    def onMessage(self, msg):
        pass


if __name__ == '__main__':

    class TestProcess (SafeProcess):

        def test(self, t):
            print("timer at", t)

        def setup(self):
            print("setup")

        def loop(self):
            print("loop-delay1")
            self.delay(0.2)
            print("loop-delay2")
            self.delay(0.2)

        def onMessage(self, msg):
            print("onMessage:", msg)

        def onExit(self):
            print("onExit")

    p = TestProcess()
    p.start()
    sleep(1)
    p.message("hello!")
    sleep(2)
    p.terminate()
    p.join()
