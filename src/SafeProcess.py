from multiprocessing import Process, Event, Queue
from queue import Empty
from time import sleep, time
import json


class SafeProcess (Process):

    _term = Event()

    _timers = []
    _callbacks = {}
    _messages = Queue()

    _delay = False

    _tid = 0

    commands = Queue()

    def __init__(self):
        super(SafeProcess, self).__init__(target=self._mainloop)
        self._term.clear()

    def _mainloop(self):
        try:
            self.setup()

            while True:
                self._checkTimers()
                self._checkMessages()
                if self._term.is_set():
                    break
                self.loop()

            self._messages.close()
            self.commands.close()
            self.onExit()
        except KeyboardInterrupt:
            pass

    def setAlarm(self, t, f):
        tid = self._tid
        self._tid += 1
        targetT = time() + t
        self._timers.append([tid, targetT])
        self.registerHandler("timer" + str(tid), f)
        return tid

    def _checkTimers(self):
        for i, timer in enumerate(self._timers):
            if time() >= timer[1]:
                self._triggerEvent("timer" + str(timer[0]), time())
                self._deleteEvent("timer" + str(timer[0]))

    def _checkMessages(self):
        while True:
            try:
                msg = self._messages.get(False)
                self._triggerEvent(msg['src'], msg)
            except Empty:
                break

    def _triggerEvent(self, event, *args):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                callback(*args)

    def registerHandler(self, src, callback):
        if src not in self._callbacks:
            self._callbacks[src] = []
        self._callbacks[src].append(callback)

    def _deleteEvent(self, event):
        if event in self._callbacks:
            del self._callbacks[event]

    def terminate(self):
        self._term.set()

    def message(self, msg):
        self._messages.put(msg)

    def send(self, dest, msg):
        cmd = {
            "dest": dest,
            "content": json.dumps(msg)
        }
        self.commands.put(cmd)

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


if __name__ == '__main__':

    class TestProcess (SafeProcess):

        def testAlarm(self, t):
            print("timer at", t)

        def setup(self):
            # 会在进程开始时运行一次
            print("setup")
            # 设一个一秒钟之后触发的 alarm，触发时调用 testAlarm
            self.setAlarm(1.0, self.testAlarm)

        def loop(self):
            # 会在进程运行过程中不断重复被调用
            print("loop-delay1")
            # delay 0.2 秒
            self.delay(0.2)
            print("loop-delay2")
            # delay 0.4 秒
            self.delay(0.4)

        def onExit(self):
            # 当本进程即将结束时，onExit 会自动被调用
            print("onExit")

    p = TestProcess()
    p.start()
    sleep(1)
    p.message("hello!")
    sleep(2)
    p.terminate()
    p.join()
