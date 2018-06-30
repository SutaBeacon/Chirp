import json
import subprocess
from queue import Empty
from glob import glob
from os.path import split
from time import time, sleep
import rtmidi
import socket

from WebSocketServer import WebSocketInServer
from WebSocketServer import WebSocketFaceServer, WebSocketControllerServer
from WebSocketServer import wsEvents, wsFaceCommands, wsControllerCommands
from HTTPServer import HTTPServer
from ConsoleLog import normal, error, notice
from InteractionController import InteractionController
from MusicAnalyzer import NoteGrouper, PhraseCutter
from UDPServer import UDPServer
from SerialServer import SerialServer


wsInServer = WebSocketInServer(8000)
wsFaceServer = WebSocketFaceServer(8001)
wsControllerServer = WebSocketControllerServer(8002)
httpServer = HTTPServer(8006)
udpServer = UDPServer()
serialServer = SerialServer()

wsInServer.start()
wsFaceServer.start()
wsControllerServer.start()
httpServer.start()
udpServer.start()

interactionController = InteractionController()

midiIn = rtmidi.RtMidiIn()
midiOut = rtmidi.RtMidiOut()
noteGrouper = NoteGrouper()
phraseCutter = PhraseCutter()

midiClock = 0
midiStartTime = time()


while not wsInServer.ready.is_set() and not wsFaceServer.ready.is_set() and not wsControllerServer.ready.is_set():
    pass
# normal("Starting browser window...")
# subprocess.call(["firefox", httpServer.address.get(), httpServer.address.get()])  # open player and controller
"""
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
"""

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
    while True:
        try:
            evt = udpServer.messages.get(False)
            if evt['cmd'] != 'time':
                interactionController.message(evt)
                noteGrouper.feed(evt)
                phraseCutter.feed(evt)
                interactionController.message(evt)
            else:
                noteGrouper.update(evt['time'])
                phraseCutter.update(evt['time'])
        except Empty:
            break
        
    
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
            udpServer.commands.put(cmd)
        elif cmd['dest'] == 'serial':
            c = bytes.fromhex('{0:02x}'.format(cmd['data']))
            serialServer.commands.put(c)

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
    if foundPiano:
        midiIn.closePort()
    if foundSynth:
        midiOut.closePort()
    wsInServer.join()
    wsFaceServer.join()
    wsControllerServer.join()
    httpServer.join()
    interactionController.terminate()
