import json
import subprocess
from queue import Empty
from glob import glob
from os.path import split
from time import sleep
import rtmidi

from WebSocketServer import WebSocketInServer
from WebSocketServer import WebSocketFaceServer, WebSocketControllerServer
from WebSocketServer import wsEvents, wsFaceCommands, wsControllerCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal, error, notice
from InteractionController import InteractionController
from MusicAnalyzer import NoteGrouper, PhraseCutter


wsInServer = WebSocketInServer(8000)
wsFaceServer = WebSocketFaceServer(8001)
wsControllerServer = WebSocketControllerServer(8002)
httpServer = HTTPServer(8003)

wsInServer.start()
wsFaceServer.start()
wsControllerServer.start()
httpServer.start()

interactionController = InteractionController()

midiIn = rtmidi.RtMidiIn()
midiOut = rtmidi.RtMidiOut()
noteGrouper = NoteGrouper()
phraseCutter = PhraseCutter()


while not wsInServer.ready.is_set() and not wsFaceServer.ready.is_set() and not wsControllerServer.ready.is_set():
    pass
normal("Starting browser window...")
subprocess.call(["open", httpServer.address.get()])  # open player
subprocess.call(["open", httpServer.address.get()])  # open controller

foundPiano = False
for i in range(midiIn.getPortCount()):
    if "SAMSON Graphite 25" in midiIn.getPortName(i):
        midiIn.openPort(i)
        foundPiano = True
        break

foundSynth = False
for i in range(midiOut.getPortCount()):
    if "FluidSynth" in midiOut.getPortName(i):
        midiOut.openPort(i)
        foundSynth = False
        break

if not foundPiano:
    error("CANNOT FIND PIANO!")
if not foundSynth:
    error("I CAN'T SING!")


def CheckWebsocketEvents(interactionController):
    try:
        evt = wsEvents.get(False)
        evt = json.loads(evt)
        evt["src"] = "websocket"
        interactionController.message(evt)
    except Empty:
        pass


def CheckSerialEvents(interactionController):
    pass


def CheckMIDIEvents(interactionController):
    if foundPiano:
        _data = midiIn.getMessage()
        if _data:
            # _time = _data[1]
            _note = _data.getNoteNumber()
            _velocity = _data.getFloatVelocity()

            if _data.isNoteOn():
                _event = 'note-on'
            elif _data.isNoteOff():
                _event = 'note-off'
            else:
                _event = 'other'

            evt = {
                'src': 'midi',
                'cmd': _event,
                'note': _note,
                'velocity': _velocity,
                # 'time': _time
            }
            print(evt)
            # noteGrouper.feed(evt)
            # phraseCutter.feed(evt)
            interactionController.message(evt)
    # noteGrouper.update(midi.time())
    # phraseCutter.update(midi.time())
    while True:
        try:
            evt = noteGrouper.messages.get(False)
            interactionController.message(evt)
        except Empty:
            break
    while True:
        try:
            evt = phraseCutter.messages.get(False)
            interactionController.message(evt)
        except Empty:
            break


def DispatchCommands(interactionController):

    def _dispatch(cmd):
        if cmd['dest'] == 'face':
            if cmd['cmd'] == 'face-change':
                try:
                    _id = animations.index(cmd['id'])
                    cmd['id'] = _id
                except ValueError:
                    error("Cannot find animation \"" + cmd['id'] + "\"")
            wsFaceCommands.put(json.dumps(cmd))
        elif cmd['dest'] == 'controller':
            wsControllerCommands.put(json.dumps(cmd))
        elif cmd['dest'] == 'midi' and midiOut:
            if cmd['cmd'] == 'instrument':
                midiOut.set_instrument(cmd['id'])
            elif cmd['cmd'] == 'note-on':
                midiOut.note_on(cmd['note'], velocity=cmd['velocity'])
            elif cmd['cmd'] == 'note-off':
                midiOut.note_off(cmd['note'])
            elif cmd['cmd'] == 'write':
                t = midi.time()
                for note in cmd['notes']:
                    note[1] += t
                midiOut.write(cmd['notes'])

    while True:
        try:
            cmd = interactionController.commands.get(False)
            _dispatch(cmd)
        except Empty:
            break


sleep(1)

animations = glob("static/animations/*.json")
for i, anim in enumerate(animations):
    animations[i] = split(anim)[-1]

cmd = {
    'cmd': 'face-load',
    'filenames': animations
}
wsFaceCommands.put(json.dumps(cmd))
wsControllerCommands.put(json.dumps(cmd))

try:
    while True:
        CheckWebsocketEvents(interactionController)
        CheckSerialEvents(interactionController)
        CheckMIDIEvents(interactionController)

        DispatchCommands(interactionController)

        interactionController.mainloop()

except KeyboardInterrupt:
    if midiIn:
        midiIn.close()
    if midiOut:
        midiOut.close()
    midi.quit()
    wsInServer.join()
    wsFaceServer.join()
    wsControllerServer.join()
    httpServer.join()
    interactionController.terminate()
