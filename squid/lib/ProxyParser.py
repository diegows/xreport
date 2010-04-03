
from datetime import datetime
from urlparse import urlparse

from squid.model.access import Address, Method, ProxyUser, ProxyStatus
from squid.model.access import HierarchyStatus, MimeType, Protocol, Domain
from squid.model.access import ServerAddress, Access, MiniAccess
from squid.model.access import DBSession
import transaction

#This must be in a configuration file
class foo(): pass
exclude = foo()
exclude.address = [ '127.0.0.1', '10.10.101.107', '10.10.101.106' ]
exclude.http_code = [ '407', '000' ]
exclude.method = [ 'ICP_QUERY' ]
exclude.protocol = [ 'cache_object' ]

class ProxyParser():
    def parse(self, line):
        fields = line.split()

        fields = line.split()
        if len(fields) != 10:
            return

        if fields[5] in exclude.method:
            return
        if fields[2] in exclude.address:
            return
        status = fields[3].split('/')
        if status[1] in exclude.http_code:
            return

        access = Access()

        log_datetime = datetime.fromtimestamp(float(fields[0]))
        access.date = log_datetime.date()
        access.time = log_datetime.time()
        access.duration = fields[1]

        access.address = Address.get(fields[2])

        access.proxy_status = ProxyStatus.get(status[0])
        access.http_code = status[1]

        size = fields[4].split('/')
        access.request_size = size[0]
        access.reply_size = size[1]

        access.method = Method.get(fields[5])

        if access.method.text == 'CONNECT':
            domain, port = fields[6].split(':')
            access.domain = Domain.get(domain)
            access.port = port
        else:
            url = urlparse(fields[6])
            if url.scheme in exclude.protocol:
                return
            access.protocol = Protocol.get(url.scheme)
            access.domain = Domain.get(url.netloc)
            if url.port:
                access.port = url.port
            else:
                access.port = 80
            access.url_path = url.path

        access.proxy_user = ProxyUser.get(fields[7])

        hierarchy = fields[8].split('/')
        access.hierarchy_status = HierarchyStatus.get(hierarchy[0])
        access.server_address = ServerAddress.get(hierarchy[1])

        access.mime_type = MimeType.get(fields[9])

        DBSession.add(access)
        MiniAccess.update(access)
        DBSession.flush()
