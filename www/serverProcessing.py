"""
Programmer: Instructor
Updates: David Beltran
File: serverProcessing.py
This file contains the credit card processing server handling web server data.
"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
import logging
import urllib.parse
import os.path
import json

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):

        request = urllib.parse.urlparse(self.path)
        file = self.directory + request.path 

        if os.path.exists(file):
            super().do_GET()
        else:
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            logging.info("File %s not found.", file)
            self._set_response()
            self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length) 
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
               str(self.path), str(self.headers), post_data.decode('utf-8'))
        
        """
        Conditional that decides if card limit is exceeded.
        Authorization code is selected depending on amount.
        """
        messageUI = json.loads(post_data.decode('utf-8'))
        accountLimit = 500.00
        authCode = 0
        amount = float(messageUI['amount'])
        if (amount > accountLimit):
            authCode = 111
        else:
            authCode = 444

        #Authorization code sent back to web server
        data = urllib.parse.urlencode({'authCode': authCode, 'amount': messageUI['amount']})
        data = data.encode('ascii')
        self._set_response()
        self.wfile.write(data)
        

def run(server_class=HTTPServer, handler_class=HTTPRequestHandler, port=8001):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
