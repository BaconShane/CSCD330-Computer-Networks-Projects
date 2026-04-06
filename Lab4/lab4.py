#author: Jake Mowatt

from sys import argv
from socket import *
from urllib.parse import urlparse

def main():
    #Checks if correct arguments are given
    #   1. -p for print, -f for file
    #   2. Target Port
    #   3. URL to retrieve
    if len(argv) != 4:
        print('Invalid Number of Arguments.')
        return
    
    FLAG = argv[1]
    PORT = int(argv[2])
    URL = argv[3]
    buffer = 4096

    #URL Parse
    parts = urlparse(URL)

    #Creates a client TCP connection
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((parts.netloc, PORT))

    #Check if the path is not empty
    path = "/"
    if (len(parts.path) != 0):
        path = parts.path
    
    #Create and send get request
    request = f"GET {path} HTTP/1.1\r\nHost: {parts.netloc}\r\nConnection: close\r\n\r\n" #Get Request made by Gemini
    clientSocket.sendall(request.encode())

    #Receive the response in chunks
    response = b""
    while True:
        data = clientSocket.recv(buffer)
        if not data:
            #No more data means the transfer is complete
            break
        response += data
    
    clientSocket.close()

    #Decode the response bytes
    response = response.decode('utf-8')

    headers, body = response.split("\r\n\r\n", 1)

    if FLAG == '-p':
        print(body, end="")
    elif FLAG == '-f':
        #print to a file
        with open('output.txt', 'w') as f:
            print(body, file=f, end="")
    else:
        print('Invalid Flag')

if __name__ == "__main__":
    main()