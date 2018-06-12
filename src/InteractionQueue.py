from multiprocessing import Queue, Event
from queue import Empty

from ConsoleLog import normal, error
from Interaction import Interaction


class InteractionQueue:

    _interactions = []
    _nextID = -1
    _current = None
    commands = Queue()

    running = Event()

    def __init__(self):
        normal("InteractionQueue running.")
        self.running.clear()

    def _assignID(self):
        self._nextID += 1
        return self._nextID

    def _getNextInteraction(self):
        if len(self._interactions) == 0:
            return (None, None)
        iid, interaction = self._interactions[0]
        self._interactions = self._interactions[1:]
        return (iid, interaction)

    def _isInteraction(self, interaction):
        if interaction is Interaction:
            return True
        if Interaction in interaction.__bases__:
            return True
        return False

    def update(self):
        # handle messages sent by interactions to be relayed
        if self._current is not None and self._current.is_alive():
            while True:
                try:
                    cmd = self._current.commands.get(False)
                    self.commands.put(cmd)
                except Empty:
                    break

        if self._current is None or not self._current.is_alive():
            iid, nextInteraction = self._getNextInteraction()
            if nextInteraction is not None:
                self._current = nextInteraction()
                self._current.start()
                self.running.set()
            else:
                self.running.clear()

    def cancel(self, id):
        _id = next((x for x in self._interactions if x[0] == id), None)
        del self._interactions[_id]

    def add(self, interaction):
        if not self._isInteraction(interaction):
            error("Item pushed onto InteractionQueue is not an Interaction!")
            return
        _id = self._assignID()
        self._interactions.append((_id, interaction))
        return _id

    def skip(self):
        if self._current is not None and self._current.is_alive():
            self._current.terminate()
            self._current.join()
            self._current = None
        self.running.clear()

    def clear(self):
        if self._current is not None and self._current.is_alive():
            self._current.terminate()
            self._current.join()
            self._current = None
            while True:
                try:
                    self._interactions.get(False)
                except Empty:
                    break
        self.running.clear()

    def isEmpty(self):
        return len(self._interactions) == 0

    def notify(self, msg):
        if self._current is not None and self._current.is_alive():
            self._current.message(msg)

    def terminate(self):
        normal("InteractionQueue shutting down.")
        self.clear()
        self.commands.close()
