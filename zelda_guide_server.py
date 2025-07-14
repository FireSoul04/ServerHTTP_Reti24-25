import sys
import mimetypes
from socket import *

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
server_address = ('localhost',serverPort)
serverSocket.bind(server_address)

serverSocket.listen(1)
print ('the web server is up on port:', serverPort)

while True:
    print ('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    print(connectionSocket, addr)
    try:
        message = connectionSocket.recv(1024)
        if len(message.split()) > 0:
            filepath = message.split()[1].decode()
            print('File requested:', filepath)
            if filepath == '/':
                filepath = '/index.html'
            
            # Determina il tipo MIME
            mimeType, _ = mimetypes.guess_type(filepath)
            print('MIME type:', mimeType)

            if mimeType == 'text/html':
                filepath = '/www' + filepath
            filepath = '.' + filepath
            print('File path:', filepath)

            with open(filepath, 'rb') as f:
                responseBody = f.read()
            
            responseHeader = 'HTTP/1.1 200 OK\r\n'
            responseHeader += f'Content-Type: {mimeType}\r\n'
            responseHeader += f'Content-Length: {len(responseBody)}\r\n'
            responseHeader += 'Connection: close\r\n'
            responseHeader += '\r\n'

            connectionSocket.send(responseHeader.encode())
            connectionSocket.send(responseBody)
            connectionSocket.close()
    except IOError:
        with open('./www/notfound.html', 'r+') as f:
            notFoundPage = f.read()

        notFoundResponse = 'HTTP/1.1 404 Not Found\r\n'
        notFoundResponse += '\r\n'
        notFoundResponse += f'{notFoundPage}\r\n'
        notFoundResponse += '\r\n'

        connectionSocket.send(notFoundResponse.encode())
        connectionSocket.close()
