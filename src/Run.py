import json
import subprocess
from queue import Empty
from glob import glob
from os.path import split
from time import sleep
import pygame.midi as midi

from WebSocketServer import WebSocketInServer
from WebSocketServer import WebSocketFaceServer, WebSocketControllerServer
from WebSocketServer import wsEvents, wsFaceCommands, wsControllerCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal, error
from InteractionController import InteractionController
from MusicAnalyzer import NoteGrouper, PhraseCutter


midi.init()

wsInServer = WebSocketInServer(8000)
wsFaceServer = WebSocketFaceServer(8001)
wsControllerServer = WebSocketControllerServer(8002)
httpServer = HTTPServer(8003)

wsInServer.start()
wsFaceServer.start()
wsControllerServer.start()
httpServer.start()

interactionController = InteractionController()

midiIn = None
noteGrouper = NoteGrouper()
phraseCutter = PhraseCutter()


while not wsInServer.ready.is_set() and not wsFaceServer.ready.is_set() and not wsControllerServer.ready.is_set():
    pass
normal("Starting browser window...")
subprocess.call(["open", httpServer.address.get()])  # open player
subprocess.call(["open", httpServer.address.get()])  # open controller


for i in range(midi.get_count()):
    if "SAMSON Graphite 25 Port1" in str(midi.get_device_info(i)[1]):
        midiIn = midi.Input(i)
        break
if midiIn is None:
    error("CANNOT FIND PIANO!")


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
    if midiIn.poll():
        _data = midiIn.read(1)[0]
        _time = _data[1]
        _event = _data[0][0]
        _note = _data[0][1]
        _velocity = _data[0][2]

        if _event == 144:
            _event = 'note-on'
        elif _event == 128:
            _event = 'note-off'
        elif _event == 208:
            _event = 'note-hold'
        else:
            _event = 'other'

        evt = {
            'src': 'midi',
            'cmd': _event,
            'note': _note,
            'velocity': _velocity,
            'time': _time
        }
        noteGrouper.feed(evt)
        phraseCutter.feed(evt)
        interactionController.message(evt)
    noteGrouper.update(midi.time())
    phraseCutter.update(midi.time())
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
            wsFaceCommands.put(cmd['content'])
        elif cmd['dest'] == 'controller':
            wsControllerCommands.put(cmd['content'])

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
    midiIn.close()
    midi.quit()
    wsInServer.join()
    wsFaceServer.join()
    wsControllerServer.join()
    httpServer.join()
    interactionController.terminate()
