#author: Jake Mowatt
from scapy.all import *
from socket import gethostbyname
from subprocess import getstatusoutput
from sys import argv

#Run whois command and parse for the AS number
def get_as(ip):
    status, output = getstatusoutput(f"whois -h riswhois.ripe.net {ip}")
    if status == 0:
        for line in output.splitlines():
            if "origin:" in line:
                parts = line.split()
                return parts[-1]
    return None

def main():
    #Checks if correct arguments are given
    #   1. Target Website
    #   2. Maximum Number of Hops
    if len(argv) != 3:
        print('Invalid Number of Arguments.')
        return
    
    target = argv[1]
    max_hops = int(argv[2])

    #Get IP from website
    try:
        target_ip = gethostbyname(target)
    except Exception:
        print(f"Error: Could not resolve {target}")
        return
    
    print(f"route to {target} ({target_ip}), {max_hops} hops max")

    traversed_as = []

    for ttl in range(1, max_hops + 1):
        #Create TCP SYN packet
        pkt = IP(dst=target_ip, ttl=ttl) / TCP(flags="S")
        response = sr1(pkt, verbose=0, timeout=3)

        if response is None:
            print(f"{ttl} - * * *")
        else:
            ip = response.src

            #Extra Credit Reverse DNS Lookup
            status, dns_output = getstatusoutput(f"host {ip}")
            hostname = ""
            if status == 0:
                hostname = f" ({dns_output.split()[-1].rstrip('.')})"

            print(f"{ttl} - {ip}{hostname}")

            #Get AS Info
            asn = get_as(ip)
            if asn and asn not in traversed_as:
                traversed_as.append(asn)
            
            #Check if target IP reached
            if ip == target_ip:
                break
    
    #Print AS path
    if traversed_as:
        print("\nTraversed AS numbers: " + " -> ".join(traversed_as))


if __name__ == "__main__":
    main()