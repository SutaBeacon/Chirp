from SafeProcess import SafeProcess


class Interaction(SafeProcess):

    def note(self, note, length, velocity=127, callback=None):
        def cb(t):
            self.send("midi", {
                "cmd": "note-off",
                "note": note
            })
            if callback:
                callback()

        self.send("midi", {
            "cmd": "note-on",
            "note": note,
            "velocity": velocity
        })

        self.setAlarm(length, cb)

    def sing(self, notes, callback=None):
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
