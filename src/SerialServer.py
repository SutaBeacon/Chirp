import serial
from serial.tools.list_ports import comports
from threading import Thread, Event

from multiprocessing import Process, Queue
from ConsoleLog import normal, error


class IncomingSerial (Thread):

    def __init__(self, port, queue):
        super(IncomingSerial, self).__init__(target=self._mainloop)
        self.port = port
        self.queue = queue
        self.terminate = Event()
    
    def _mainloop(self):
        while not self.terminate.is_set():
            ch = self.port.read()
            normal("got:", ch.decode('utf-8'))
            self.queue.put(ch.decode('utf-8'))


class SerialServer (Process):
    
    messages = Queue()
    commands = Queue()
    port = None

    def __init__(self, port=None):
        super(SerialServer, self).__init__(target=self._mainloop)
        if port:
            try:
                self.port = serial.Serial(port, 9600)
            except serial.serialutil.SerialException:
                error("Can't open given port", port)
        else:
            ports = comports()
            for port in ports:
                if port.usb_description() and "Arduino" in port.usb_description():
                    try:
                        self.port = serial.Serial(port.device, 9600)
                        self.incoming = IncomingSerial(self.port, self.messages)
                        self.incoming.start()
                        return
                    except serial.serialutil.SerialException:
                        error("Can't open port", port.device, "-", port.usb_description())
                    break
            error("Can't find arduino")
            

    def _mainloop(self):
        if not self.port:
            return
        while True:
            try:
                ch = self.commands.get()
                normal("command:", ch)
                self.port.write(ch.encode('utf-8'))
            except KeyboardInterrupt:
                if self.port:
                    normal("Close serial port.")
                    self.port.close()
                    self.incoming.terminate.set()
                    self.incoming.join()
                break

    def message(self, msg):
        pass
        # if msg['cmd'] == ''


if __name__ == '__main__':
    ss = SerialServer()
    ss.start()
    try:
        while True:
            ch = input("Input command: ")
            ss.commands.put(ch)
    except KeyboardInterrupt:
        pass