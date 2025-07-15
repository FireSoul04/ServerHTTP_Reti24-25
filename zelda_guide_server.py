import sys
import mimetypes
import logging
from socket import *

def setupLogger(name, logFile):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logConsoleHandler = logging.StreamHandler(sys.stdout)
    logFileHandler = logging.FileHandler(logFile)
    formatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s]:  %(message)s')
    logConsoleHandler.setFormatter(formatter)
    logFileHandler.setFormatter(formatter)
    logger.addHandler(logConsoleHandler)
    logger.addHandler(logFileHandler)
    return logger

def sendResponse(socket, status, contentType, content, logger):
    responseHeader = f'HTTP/1.1 {status}\r\n'
    responseHeader += f'Content-Type: {contentType}\r\n'
    responseHeader += f'Content-Length: {len(content)}\r\n'
    responseHeader += 'Connection: close\r\n'
    responseHeader += '\r\n'

    try:
        socket.sendall(responseHeader.encode('utf-8'))
        socket.sendall(content)
    except ConnectionAbortedError:
        logger.error('ConnectionAbortedError: client closed the connection before send completed')
    except Exception as e:
        logger.critical('Unexpected send error: ' + e)

logger = setupLogger("ServerLogger", "log/server.log")
serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverAddress = ('localhost', serverPort)
serverSocket.bind(serverAddress)

serverSocket.listen(1)
logger.info('The web server is up on port: ' + str(serverPort))

while True:
    logger.info('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    logger.info("Connected with: " + addr[0] + ":" + str(addr[1]))
    try:
        message = connectionSocket.recv(1024)
        if len(message.split()) > 0:
            filepath = message.split()[1].decode()
            logger.info('File requested: ' + filepath)
            if filepath == '/':
                filepath = '/index.html'
            
            # Determina il tipo MIME
            mimeType, _ = mimetypes.guess_type(filepath)
            logger.info('MIME type: ' + mimeType)

            if mimeType is None:
                mimeType = 'application/octet-stream'
                logger.info('Defaulting to application/octet-stream for unknown MIME type')
            elif mimeType == 'text/html':
                filepath = '/www' + filepath
            filepath = '.' + filepath

            with open(filepath, 'rb') as f:
                responseBody = f.read()
                
            sendResponse(connectionSocket, '200 OK', mimeType, responseBody, logger)
        else:
            sendResponse(connectionSocket, '400 Bad Request', 'text/plain', 'Bad Request'.encode('utf-8'), logger)
    except FileNotFoundError:
        with open('./www/notfound.html', 'rb') as f:
            notFoundPage = f.read()

        sendResponse(connectionSocket, '404 Not Found', 'text/html', notFoundPage, logger)
    except Exception as e:
        logger.critical('Unexpected error: ' + e)
        sendResponse(connectionSocket, '500 Internal Server Error', 'text/plain', 'Internal Server Error'.encode('utf-8'), logger)

    connectionSocket.close()