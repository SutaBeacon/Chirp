import http.server
import socketserver
from multiprocessing import Process, Queue

from ConsoleLog import normal, success, error


class HTTPServer(Process):

    address = Queue()

    def __init__(self, port):
        super(HTTPServer, self).__init__()
        self.PORT = port
        self.handler = http.server.SimpleHTTPRequestHandler

    def run(self):
        normal("Starting HTTP Server...")

        while True:
            try:
                httpd = socketserver.TCPServer(('', self.PORT), self.handler)
                success("Serving at port", self.PORT)
                try:
                    self.address.put("http://127.0.0.1:" + str(self.PORT) + "/static/")
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    normal("Shutting down HTTP server.")
                    httpd.server_close()
                    success("HTTP server shut down.")
            except socketserver.socket.error as exc:
                if exc.args[0] != 48:
                    raise
                error('Port', self.PORT, 'already in use')
                self.PORT += 1
            else:
                break


if __name__ == '__main__':
    server = HTTPServer(8001)
    server.start()
    try:
        server.join()
    except KeyboardInterrupt:
        pass
