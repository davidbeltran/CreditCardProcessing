"""
Programmer: Instructor
Updates: David Beltran
File: serverUI.py
This file contains the UI web server handling web page inputs.
"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
import logging
import urllib.parse
import os.path
import requests

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
        
        #User input turned into JSON format
        post_data = post_data.decode('utf-8')
        post_data = self.__getJson(post_data)
        
        url ='http://localhost:8001'
        r = requests.post(url, json = post_data)

        """
        Conditional statement to decide what message to send to web page dependant
        on processing server
        """
        authMessage = ""
        response = self.__getJson(r.text)
        if (response['authCode'] == "111"):
            authMessage = f"Transaction for ${response['amount']} was declined"
        elif (response['authCode'] == "444"):
            authMessage = f"Transaction for ${response['amount']} was accepted"

        #Message sent to web page
        self._set_response()
        self.wfile.write(bytes(authMessage, 'utf-8'))

    """
    Private method to turn web page input into a dictionary for JSON format communication
    """
    def __getJson(self, message):
        return dict((a.strip(), b.strip())
                        for a, b in (element.split('=')
                                    for element in message.split('&')))

def run(server_class=HTTPServer, handler_class=HTTPRequestHandler, port=8000):
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
