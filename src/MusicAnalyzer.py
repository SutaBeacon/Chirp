from textdistance import jaccard
from queue import Queue

from data.phrases import Phrases


def similarity(phrase1, phrase2):
    s1 = ""
    s2 = ""
    for note in phrase1:
        s1 += chr(note)
    for note in phrase2:
        s2 += chr(note)
    return jaccard(s1, s2)


def predict(phrase):
    ph = Phrases[:]
    ph.sort(key=lambda x: similarity(x[1], phrase))
    return (ph[-1], similarity(ph[-1][1], phrase))


class NoteGrouper:

    notes = []
    messages = Queue()
    start = 0
    _thres = 50

    def feed(self, note):
        if note['cmd'] == 'note-on':
            if len(self.notes) == 0:
                self.notes.append(note['note'])
                self.start = note['time']
            else:
                if note['time'] - self.start > self._thres:
                    # Chord ended!
                    evt = {
                        'src': 'midi',
                        'cmd': 'note-group',
                        'notes': self.notes,
                        'time': self.start
                    }
                    self.messages.put(evt)
                    self.notes = [note['note']]
                    self.start = note['time']
                else:
                    self.notes.append(note['note'])

    def update(self, time):
        if time - self.start > self._thres and len(self.notes) > 0:
            # Chord ended!
            evt = {
                'src': 'midi',
                'cmd': 'note-group',
                'notes': self.notes,
                'time': self.start
            }
            self.messages.put(evt)
            self.notes = []
            self.start = 0


class PhraseCutter:

    notes = []
    messages = Queue()
    start = 0
    end = 0
    _thres = 400

    count = 0

    def feed(self, note):
        if note['cmd'] == 'note-on':
            if len(self.notes) == 0:
                self.notes.append(note['note'])
                self.start = note['time']
                self.end = note['time'] + 50000
                self.count = 1
                evt = {
                    'src': 'midi',
                    'cmd': 'phrase-start',
                    'notes': self.notes
                }
                self.messages.put(evt)
            else:
                if note['time'] - self.end > self._thres and self.count == 0:
                    # Chord ended!
                    evt = {
                        'src': 'midi',
                        'cmd': 'phrase-end',
                        'notes': self.notes,
                        'start': self.start,
                        'end': self.end
                    }
                    self.messages.put(evt)
                    self.notes = [note['note']]
                    self.start = note['time']
                    self.end = note['time'] + 50000
                else:
                    self.notes.append(note['note'])
                    self.count += 1
                    evt = {
                        'src': 'midi',
                        'cmd': 'phrase',
                        'notes': self.notes
                    }
                    self.messages.put(evt)
        elif note['cmd'] == 'note-off':
            self.end = note['time']
            self.count -= 1

    def update(self, time):
        if time - self.end > self._thres and len(self.notes) > 0 and self.count == 0:
            # Chord ended!
            evt = {
                'src': 'midi',
                'cmd': 'phrase-end',
                'notes': self.notes,
                'start': self.start,
                'end': self.end
            }
            self.messages.put(evt)
            self.notes = []
            self.start = 0
