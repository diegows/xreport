
import os
import sys
import ConfigParser

from sqlalchemy import create_engine
from genshi.template import MarkupTemplate, TemplateLoader
import tg
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from squid.model import init_model
from squid.lib.ProxyParser import ProxyParser

config = ConfigParser.ConfigParser( { 'here' : os.getcwd() } )
config.read(os.path.join(os.getcwd(), 'development.ini'))
sqlalchemy_url = config.get('app:main', 'sqlalchemy.url')
engine = create_engine(sqlalchemy_url, echo = False)
init_model(engine)

parser = ProxyParser()

class ProxyUDPLog(DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        for line in data.split('\n'):
            if len(line) == 0:
                continue
            print line
            parser.parse(line)

file = sys.argv[1]

if file.startswith('udp:'):
    port = file.split(':')[1]
    port = int(port)

    reactor.listenUDP(port, ProxyUDPLog())
    reactor.run()
    sys.exit(0)


access_log = open(file)

while True:
    line = access_log.readline()
    if not line:
        break

    parser.parse(line)
