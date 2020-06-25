import webbrowser
import threading
import http.server
import json

class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    callback = lambda: b""
    @classmethod
    def set_callback(cls, callback):
        cls.callback = callback

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str.encode(json.dumps(HTTPHandler.callback())))

def web_monitor(analyzer, PORT=8000):
    HTTPHandler.set_callback(analyzer)
    httpd = http.server.HTTPServer(("", PORT), HTTPHandler)
    print("Server started at localhost:" + str(PORT))
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    webbrowser.open_new(f'http://localhost:{PORT}/')
    thread.start()