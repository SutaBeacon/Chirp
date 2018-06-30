from Interaction import Interaction
from ConsoleLog import notice
from data.phrases import question
import random


class Duet(Interaction):

    phrase = []

    def setup(self):
        self.registerHandler('midi', self.onMidi)
        self.setInstrument(73)
        self.makeFace('happy_open.json')
        self.sing(question)

    def onMidi(self, msg):
        # notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
        if msg['cmd'] == 'note-on':
            self.phrase.append(msg)
        if msg['cmd'] == 'phrase-end':
            self.makeFace('laugh.json')
            startTime = self.phrase[0]['time']
            notes = [note['note'] for note in self.phrase]
            final = []
            for i, note in enumerate(self.phrase):
                self.phrase[i]['time'] -= startTime
                self.phrase[i]['note'] = random.choice(notes)
                n = []
                n.append(0x90)
                n.append(self.phrase[i]['note'])
                n.append(127)
                final.append([n, self.phrase[i]['time']])
                n[0] = 0x80
                if i < len(self.phrase)-1:
                    final.append([n, self.phrase[i + 1]['time']])
                else:
                    final.append([n, self.phrase[i]['time'] + 1000])
            self.sing(final)
            self.phrase = []

            

    def finish(self, t):
        self.terminate()
