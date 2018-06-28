from SafeProcess import SafeProcess


class Interaction(SafeProcess):

    def makeFace(self, name):
        self.send("face", {
            "cmd": "face-change",
            "id": name
        })

    def setInstrument(self, instrument=73):
        self.send("midi", {
            "cmd": "instrument",
            "id": instrument
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
