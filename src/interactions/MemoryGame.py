import random

from Interaction import Interaction
from data.phrases import question
from ConsoleLog import notice, normal


class MemoryGame (Interaction):

    errorRate = 0.15

    notes = [0, 0, 0]

    state = "init"

    currentPhrase = []

    turn = 'player'
    playerScore = 0
    chirpScore = 0

    inputCounter = 0
    noteCount = 4

    gameCount = 0

    started = False

    lastTime = 0

    newSequence = False

    def generatePhrase(self, src, length):
        result = []
        for i in range(length):
            result.append(random.choice(src))
        return result


    def setup(self):
        self.makeFace("happy_open.json")
        self.registerHandler('midi', self.onMidi)
        self.state = "config-1"
        self.oniSetAllLED(0)
        self.servoAngle(140)
        self.oniSetLED(0, 1)
        self.delay(3)
        self.makeFace('hint.json')

    def loop(self):

        if self.newSequence:
            normal("NEW_SEQ")
            self.newSequence = False
            self.currentPhrase = self.generatePhrase(self.notes, self.noteCount)
            self.noteCount += 1
            for note in self.currentPhrase:
                self.delay(1)
                self.oniMakeNote(note)
            self.delay(1)


    def onMidi(self, msg):
        # normal(msg)
        if msg['cmd'] == 'note-on':
            if self.lastTime == msg['time']:
                self.lastTime = msg['time']
                return
            self.lastTime = msg['time']
            notice(self.state)
            if self.state == 'config-1':
                normal("CONF_1")
                if msg['note'] in self.notes:
                    self.makeFace("nono.json")
                else:
                    self.oniSetLED(0, 2)
                    self.oniSetLED(1, 1)
                    self.makeFace("hint.json")
                    self.state = 'config-2'
                    self.notes[0] = msg['note']
                return
            
            elif self.state == 'config-2':
                normal("CONF_2")
                if msg['note'] in self.notes:
                    self.makeFace("serious-1.json")
                else:
                    self.oniSetLED(1, 2)
                    self.oniSetLED(2, 1)
                    self.makeFace("hint.json")
                    self.state = 'config-3'
                    self.notes[1] = msg['note']
                return
            
            elif self.state == 'config-3':
                normal("CONF_3")
                if msg['note'] in self.notes:
                    self.makeFace("nono.json")
                else:
                    self.oniSetLED(2, 2)
                    self.makeFace("hint.json")
                    self.delay(0.3)
                    self.notes[2] = msg['note']
                    self.makeFace('happy_open.json')
                    self.delay(1)
                    self.makeFace('serious-2.json')
                    self.setAlarm(5, self.hint)
                    self.state = 'playing'

                    self.started = True

                    self.newSequence = True
                return

            elif self.state == 'playing' and self.started:
                normal("NOTE_INPUT")
                normal(self.inputCounter)
                normal(self.currentPhrase[self.inputCounter])
                if msg['note'] == self.currentPhrase[self.inputCounter]:
                    # player correctly inputs a note
                    self.inputCounter += 1
                    if self.noteCount == self.inputCounter + 1:
                        # player gets a point
                        normal("PLAYER SCORES")
                        self.inputCounter = 0
                        self.playerScore += 1
                        if self.playerScore == 2:
                            # player wins!
                            self.win('player')
                            return
                        self.oniShowPoints(self.playerScore, self.chirpScore)
                        # chirp is not happy about this
                        self.delay(0.3)
                        self.makeFace('pityful.json')
                        self.delay(0.5)
                        self.makeFace('serious-1.json')
                        # chirp's turn
                        self.delay(1)

                        mistake = False
                        for note in self.currentPhrase:
                            normal("Chirp plays")
                            if random.random() < self.errorRate:
                                # chirp "decides" to make a mistake
                                self.makeFace('laugh.json')
                                n = random.choice(self.notes)
                                while n == note:
                                    n = random.choice(self.notes)
                                self.noteDelay(n, 0.6)
                                self.makeFace('serious-1.json')
                                self.delay(0.4)
                                # The mistake is made
                                mistake = True 
                                break
                            else:
                                self.makeFace('laugh.json')
                                self.noteDelay(note, 0.6)
                                self.makeFace('serious-1.json')
                                self.delay(0.4)
                        
                        if mistake:
                            # a mistake was made!
                            self.oniFail()
                            self.makeFace('pityful.json')
                            self.delay(0.5)
                            self.makeFace('nono.json')
                            self.delay(1.5)
                            self.makeFace('serious-1.json')
                        else:
                            self.oniSuccess()
                            self.makeFace('laugh.json')
                            self.delay(1.5)
                            self.chirpScore += 1
                            if self.chirpScore == 2:
                                # chirp wins!
                                self.win('chirp')
                                return
                        self.newSequence = True
                    self.oniShowPoints(self.playerScore, self.chirpScore)
                                
                else:
                    # player fails
                    self.oniFail()
                    self.makeFace('laugh.json')
                    self.delay(1.5)

                    # chirp's turn
                    self.delay(1)

                    mistake = False
                    for note in self.currentPhrase:
                        if random.random() < self.errorRate:
                            # chirp "decides" to make a mistake
                            self.makeFace('laugh.json')
                            n = random.choice(self.notes)
                            while n == note:
                                n = random.choice(self.notes)
                            self.noteDelay(n, 0.6)
                            self.makeFace('serious-1.json')
                            self.delay(0.4)
                            # The mistake is made
                            mistake = True 
                            break
                        else:
                            self.makeFace('laugh.json')
                            self.noteDelay(note, 0.6)
                            self.makeFace('serious-1.json')
                            self.delay(0.4)
                    
                    if mistake:
                        # a mistake was made!
                        self.oniFail()
                        self.makeFace('pityful.json')
                        self.delay(0.5)
                        self.makeFace('nono.json')
                        self.delay(1.5)
                        self.makeFace('serious-1.json')
                    else:
                        self.oniSuccess()
                        self.makeFace('laugh.json')
                        self.delay(1.5)
                        self.chirpScore += 1
                        if self.chirpScore == 2:
                            # chirp wins!
                            self.win('chirp')
                            return
                    self.newSequence = True
                self.oniShowPoints(self.playerScore, self.chirpScore)
                return
                        
    def singSequence(self, seq):
        for note in seq:
            self.makeFace('laugh.json')
            self.makeNote(note, 600, callback=self.serious)
            
    def oniFail(self):
        self.oniSetAllLED(1)
        self.delay(0.2)
        self.oniSetAllLED(0)
        self.delay(0.2)
        self.oniSetAllLED(1)
        self.delay(0.2)
        self.oniSetAllLED(0)
        self.delay(0.2)

    def oniSuccess(self):
        self.oniSetAllLED(2)
        self.delay(0.2)
        self.oniSetAllLED(0)
        self.delay(0.2)
        self.oniSetAllLED(2)
        self.delay(0.2)
        self.oniMakeNote(67)
        self.oniSetAllLED(0)
        self.delay(0.2)

    def win(self, who):
        if who == 'player':
            self.oniSuccess()
            self.servoAngle(140)
            self.makeFace('grumpy.json')
            self.delay(0.8)
            self.servoAngle(150)
            self.delay(1)
            pass
        elif who == 'chirp':
            self.oniFail()
            self.makeFace('laugh.json')
            self.delay(0.7)
            self.makeFace('startgame.json')
            self.delay(0.5)
            self.makeFace('laugh.json')
        self.delay(2)
        self.servoAngle(140)
        self.makeFace('wakeup.json')
        self.terminate()

    def hint(self, t):
        self.makeFace('hint.json')

    def serious(self, t):
        self.faceFace('serious-1.json')

                
