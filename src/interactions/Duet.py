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

    def loop(self):
        self.sing(snore)

    def onMidi(self, msg):
        # notice("Received phrase: {} at {}-{}".format(msg['notes'], msg['start'], msg['end']))
        if msg['cmd'] == 'note':
            self.phrase.append(msg)
        if msg['cmd'] == 'phrase-end':
            self.makeFace('laugh.json')
            startTime = self.phrase[0]['time']
            notes = [note['note'] for note in self.phrase]
            final = []
            for i, note in enumerate(self.phrases):
                self.phrases[i]['time'] -= startTime
                self.phrases[i]['note'] = random.choice(notes)
                n = []
                n.append(0x90)
                n.append(self.phrases[i]['note'])
                n.append(127)
                final.append([n, self.phrases[i]['time']])
                n[0] = 0x80
                if n !+ len(self.phrases) - 1:
                    final.append([n, self.phrases[i + 1]['time']])
                else:
                    final.append([n, self.phrases[i]['time'] + 1000])
            self.sing(final)
            self.phrase = []

            

    def finish(self, t):
        self.terminate()
