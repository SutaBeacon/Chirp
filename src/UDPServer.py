import socket
import json
from threading import Thread, Event

from multiprocessing import Process, Queue
from ConsoleLog import normal, error


class IncomingUDP (Thread):

    terminate = Event()

    def __init__(self, queue):
        super(IncomingUDP, self).__init__(target=self._mainloop)
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(('0.0.0.0', 8766))
        self.queue = queue
    
    def _mainloop(self):
        while not self.terminate.is_set():
            data = self.serverSocket.recv(4096)
            self.queue.put(json.loads(data.decode('utf-8')))


class UDPServer (Process):
    
    messages = Queue()
    commands = Queue()
    port = None

    def __init__(self, port=None):
        super(UDPServer, self).__init__(target=self._mainloop)
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.incoming = IncomingUDP(self.messages)
        self.incoming.start()
            

    def _mainloop(self):
        while True:
            try:
                cmd = self.commands.get()
                print(cmd)
                self.clientSocket.sendto(json.dumps(cmd).encode('utf-8'), ('192.168.124.10', 8765)) # production: 7
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    ss = UDPServer()
    ss.start()
    ss.join()