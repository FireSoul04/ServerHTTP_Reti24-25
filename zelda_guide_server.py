import sys
import mimetypes
from socket import *

def sendResponse(socket, status, contentType, content):
    responseHeader = f'HTTP/1.1 {status}\r\n'
    responseHeader += f'Content-Type: {contentType}\r\n'
    responseHeader += f'Content-Length: {len(content)}\r\n'
    responseHeader += 'Connection: close\r\n'
    responseHeader += '\r\n'

    try:
        socket.sendall(responseHeader.encode('utf-8'))
        socket.sendall(content)
    except ConnectionAbortedError:
        print('ConnectionAbortedError: client closed the connection before send completed')
    except Exception as e:
        print('Unexpected send error:', e)

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

            if mimeType is None:
                mimeType = 'application/octet-stream'
                print('Defaulting to application/octet-stream for unknown MIME type')
            elif mimeType == 'text/html':
                filepath = '/www' + filepath
            filepath = '.' + filepath
            print('File path:', filepath)

            with open(filepath, 'rb') as f:
                responseBody = f.read()
                
            sendResponse(connectionSocket, '200 OK', mimeType, responseBody)
        else:
            sendResponse(connectionSocket, '400 Bad Request', 'text/plain', 'Bad Request'.encode('utf-8'))
    except FileNotFoundError:
        with open('./www/notfound.html', 'rb') as f:
            notFoundPage = f.read()

        sendResponse(connectionSocket, '404 Not Found', 'text/html', notFoundPage)
    except Exception as e:
        print('Unexpected error:', e)
        sendResponse(connectionSocket, '500 Internal Server Error', 'text/plain', 'Internal Server Error'.encode('utf-8'))

    connectionSocket.close()