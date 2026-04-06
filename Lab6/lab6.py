#author: Jake Mowatt
from urllib.parse import urlparse
from random import randint
from scapy.all import *
from socket import gethostbyname
from sys import argv

def main():
    #Checks if URL is provided
    if len(argv) != 2:
        print('Invalid Number of Arguments.')
        return
    
    #URL and Network setup
    URL = argv[1]
    URLparts = urlparse(URL)
    host = URLparts.hostname
    path = URLparts.path if URLparts.path else "/"
    src_port = randint(1024, 65535)
    dst_port = 80
    dst_ip = socket.gethostbyname(host)

    #Step 1: Send SYN (Used Gemini for help)
    syn = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags="S", seq=4)
    syn_ack = sr1(syn, timeout=2, verbose=0)

    if syn_ack and syn_ack.haslayer(TCP) and syn_ack[TCP].flags == "SA":

        #Step 2: Receive SYN/ACK (Referenced Gemini for help)
        my_ack = syn_ack.seq + 1
        my_seq = syn_ack.ack

        #Prepare ACK
        ack = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags="A", seq=my_seq, ack=my_ack)

        #Step 3: Send ACK
        send(ack, verbose=0)
    else:
        return

    #GET Request
    get_request = (f"GET {path} HTTP/1.1\r\n"f"Host: {host}\r\n""Connection: close\r\n\r\n")

    #GET Packet
    get_packet = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags="PA", seq=my_seq, ack=my_ack) / get_request

    #Send request and receive response
    response = sr1(get_packet, timeout=2, verbose=0)

    #If (Help from Gemini)
    if response:
        #Increment sequence by get
        my_seq += len(get_request)
        # Increment your ACK by the size of the data the server sent back
        # If there's no data, we still increment by 1 for the packet itself
        data_len = len(response[TCP].payload) if response.haslayer(Raw) else 0
        my_ack = response.seq + max(1, data_len)

    #Step 4: Creat FIN Packet
    fin_packet = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags="FA", seq=my_seq, ack=my_ack)
    fin_ack_response = sr1(fin_packet, verbose=0, timeout=2)

    if fin_ack_response:
            #Step 5: Send final ACK
            last_ack = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags="A", seq=fin_ack_response.ack, ack=fin_ack_response.seq + 1)
            send(last_ack, verbose=0)
                               
if __name__ == "__main__":
    main()