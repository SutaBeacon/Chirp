from SafeProcess import SafeProcess


class Interaction(SafeProcess):

    def makeFace(self, name):
        print(name)
        self.send("face", {
            "cmd": "face-change",
            "id": name
        })

    def setInstrument(self, instrument=73):
        self.send("midi", {
            "cmd": "instrument",
            "id": instrument
        })

    def noteDelay(self, note, length):
        self.send("midi", {
            "cmd": "note-on",
            "note": note,
            "velocity": 127
        })
        self.delay(length)
        self.send("midi", {
            "cmd": "note-off",
            "note": note
        })


    def makeNote(self, note, length, velocity=127, callback=None, after=None):
        def cb(t):
            self.send("midi", {
                "cmd": "note-off",
                "note": note
            })
            if callback:
                callback()
            if after:
                self.triggerEvent(after)

        self.send("midi", {
            "cmd": "note-on",
            "note": note,
            "velocity": velocity
        })

        self.setAlarm(length, cb)

    def sing(self, notes, callback=None, after=None):
        tmax = 0
        for note in notes:
            t = note[1]
            if t > tmax:
                tmax = t
        self.send("midi", {
            "cmd": "write",
            "notes": notes
        })
        if callback:
            self.setAlarm(tmax / 1000, callback)

        if after:
            def _cb(t):
                self.triggerEvent(after)
            self.setAlarm(tmax / 1000, _cb)

    def oniSetLED(self, ind, num):
        self.send("serial", {
            'data': ind * 4 + num
        })

    def oniMakeNote(self, note):
        self.send("serial", {
            'data': note - 24
        })

    def oniShowPoints(self, playerScore, chirpScore):
        for i in range(3):
            self.oniSetLED(i, 0)
        for i in range(playerScore):
            self.oniSetLED(i, 2)
        for i in range(chirpScore):
            self.oniSetLED(3 - i, 1)

    def oniSetAllLED(self, num):
        for i in range(3):
            self.oniSetLED(i, num)

    def servoAngle(self, angle):
        self.send("serial", {
            'data': angle
        })

if __name__ == '__main__':

    from time import sleep

    class TestInteraction(Interaction):
        def testAlarm(self, t):
            print("timer at", t)

        def setup(self):
            # 会在进程开始时运行一次
            print("setup")
            # 设一个一秒钟之后触发的 alarm，触发时调用 testAlarm
            self.setAlarm(1.5, self.testAlarm)
            self.registerHandler('midi', self.onMidi)

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

        def onMidi(self, msg):
            print(msg)
    

    p = TestInteraction()
    p.start()
    sleep(1)
    p.message({
        'src': 'midi',
        'cmd': 'note-on',
        'note': 64,
        'time': 1239
    })
    sleep(2)
    p.terminate()
    p.join()