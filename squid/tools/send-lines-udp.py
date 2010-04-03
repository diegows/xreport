
import sys
from socket import *

file = open(sys.argv[1])

udp_sock = socket(AF_INET, SOCK_DGRAM)

for line in file:
    if not line:
        break

    line = line[:-1]

    udp_sock.sendto(line, ('localhost', 9999))
