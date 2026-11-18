from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Hello, world\n')

        elif self.path == '/status':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK\n')

        elif self.path == '/read':
            # Reads a file from disk — introduces openat/read/close syscalls
            # into the trace, adding variation to the normal database
            try:
                with open('/etc/hostname', 'r') as f:
                    data = f.read().encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(500)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found\n')

    def log_message(self, format, *args):
        # Suppress access logs so they don't clutter the terminal
        pass

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), SimpleHandler)
    print('Server running on port 8080')
    server.serve_forever()
