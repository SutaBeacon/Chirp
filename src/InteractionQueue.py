from multiprocessing import Process, Lock, Queue, Event
from queue import Empty
import time

from ConsoleLog import normal, success, error, warning
from Interaction import Interaction


class InteractionQueue(Process):

    _interactions = Queue()
    _nextID = -1
    _current = None
    _lock = Lock()
    _terminate = Event()
    _skip = Event()
    _clear = Event()
    _canceling = Queue()
    _canceled = []
    _empty = Event()
    _messages = Queue()
    commands = Queue()

    running = Event()

    def _assignID(self):
        self._nextID += 1
        return self._nextID

    def _getNextInteraction(self):
        try:
            iid, interaction = self._interactions.get(False)
        except Empty:
            return (None, None)

        while iid in self._canceled:
            _id = self._canceled.index(iid)
            del self._canceled[_id]
            try:
                iid, interaction = self._interactions.get(False)
            except Empty:
                return (None, None)
        return (iid, interaction)

    def _isInteraction(self, interaction):
        if interaction is Interaction:
            return True
        if Interaction in interaction.__bases__:
            return True
        return False

    def run(self):
        normal("InteractionQueue running.")
        self._terminate.clear()
        self.running.clear()
        try:
            while True:
                # get interaction ids to be canceled
                while True:
                    try:
                        _id = self._canceling.get(False)
                        if _id not in self._canceled:
                            self._canceled.append(_id)
                    except Empty:
                        break

                # handle notifications
                while True:
                    try:
                        msg = self._messages.get(False)
                        if self._current is not None and self._current.is_alive():
                            self._current.message(msg)
                    except Empty:
                        break

                # handle messages sent by interactions to be relayed
                if self._current is not None and self._current.is_alive():
                    while True:
                        try:
                            cmd = self._current.commands.get(False)
                            self.commands.put(cmd)
                        except Empty:
                            break

                # handle skipping and clearing
                if self._skip.is_set():
                    if self._current is not None and self._current.is_alive():
                        self._skip.clear()
                        self._current.terminate()
                        self._current.join()
                        self._current = None
                    if self._clear.is_set():
                        while True:
                            try:
                                self._interactions.get(False)
                            except Empty:
                                break
                        self._clear.clear()
                    self.running.clear()

                # handle skipping and clearing
                if self._current is None or not self._current.is_alive():
                    iid, nextInteraction = self._getNextInteraction()
                    if nextInteraction is not None:
                        self._empty.clear()
                        self._current = nextInteraction()
                        self._current.start()
                        self.running.set()
                    else:
                        self._empty.set()
                        self.running.clear()
        except KeyboardInterrupt:
            pass

    def cancel(self, id):
        self._canceling.put(id)

    def add(self, interaction):
        while self._clear.is_set():
            pass
        if not self._isInteraction(interaction):
            error("Item pushed onto InteractionQueue is not an Interaction!")
            return
        _id = self._assignID()
        self._interactions.put((_id, interaction))
        return _id

    def skip(self):
        self._skip.set()

    def clear(self):
        self._clear.set()
        self._skip.set()

    def isEmpty(self):
        return self._empty.is_set()

    def notify(self, msg):
        self._messages.put(msg)

    def terminate(self):
        normal("InteractionQueue shutting down.")
        self._clear.set()
        self._skip.set()
        self._interactions.close()
        self._canceling.close()
        self._messages.close()
        self.commands.close()
        self._terminate.set()


if __name__ == '__main__':

    class TestInteraction1(Interaction):
        counter = 0

        def setup(self):
            success("Interaction 1 running!")

        def loop(self):
            normal("Interaction 1.")
            self.counter += 1
            self.delay(1.0)
            if self.counter == 6:
                self.terminate()

    class TestInteraction2(Interaction):
        counter = 0

        def setup(self):
            success("Interaction 2 running!")

        def loop(self):
            normal("Interaction 2.")
            self.counter += 1
            self.delay(1.0)
            if self.counter == 6:
                self.terminate()

    class TestInteraction3(Interaction):
        counter = 0

        def setup(self):
            success("Interaction 3 running!")

        def loop(self):
            normal("Interaction 3.")
            self.counter += 1
            self.delay(1.0)
            if self.counter == 6:
                self.terminate()

    iq = InteractionQueue()

    iq.add(TestInteraction1)

    iq.start()

    time.sleep(1)
    print("adding")
    _id = iq.add(TestInteraction2)
    iq.add(TestInteraction3)

    time.sleep(1)
    print("canceling")
    iq.cancel(_id)
    time.sleep(1)
    print("skipping")
    iq.skip()
    time.sleep(4)
    iq.clear()
    time.sleep(1)
    print("adding")
    iq.add(TestInteraction2)

    iq.join()
