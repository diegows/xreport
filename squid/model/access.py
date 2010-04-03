# -*- coding: utf-8 -*-
"""Squid model."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from squid.model import DeclarativeBase, metadata, DBSession

#Check incoming garbage here, in each FK definition.
#ForeignValues should call a method in the child class to do it

fk_cache = {}

class ForeignValues():
    @classmethod
    def get(cls, text):
        cls.check(text)

        if fk_cache.has_key(cls) and fk_cache[cls].has_key(text):
            return fk_cache[cls][text]

        query = DBSession.query(cls)
        query._autoflush = False
        data = query.filter(cls.text == text).all()
        if len(data) == 0:
            data = cls()
            data.text = text
            DBSession.add(data)
        elif len(data) == 1:
            data = data[0]
        else:
            #XXX: do this better
            raise Exception()

        if not fk_cache.has_key(cls):
            fk_cache[cls] = {}
        fk_cache[cls][text] = data
        return data

    @classmethod
    def check(cls, check):
        """
        Each class should implement this function to check if the text format
        is valid. Raise an exception on failure.
        """
        return True

    def __repr__(self):
        print self.text

    def __str__(self):
        print self.text

class Address(DeclarativeBase, ForeignValues):
    __tablename__ = 'address'

    id = Column(Integer(), primary_key = True)
    text = Column(String(16), nullable = False, unique = True)

class Method(DeclarativeBase, ForeignValues):
    __tablename__ = 'methods'

    id = Column(Integer(), primary_key = True)
    text = Column(String(20), nullable = False, unique = True)

class ProxyUser(DeclarativeBase, ForeignValues):
    __tablename__ = 'proxy_users'

    id = Column(Integer(), primary_key = True)
    text = Column(String(32), nullable = False, unique = True)
    fullname = Column(String(120), nullable = True)
    location = Column(String(120), nullable = True)

class ProxyStatus(DeclarativeBase, ForeignValues):
    __tablename__ = 'proxy_status'

    id = Column(Integer(), primary_key = True)
    text = Column(String(32), nullable = False, unique = True)

class HierarchyStatus(DeclarativeBase, ForeignValues):
    __tablename__ = 'hierarchy_status'

    id = Column(Integer(), primary_key = True)
    text = Column(String(32), nullable = False, unique = True)

class MimeType(DeclarativeBase, ForeignValues):
    __tablename__ = 'mime_types'

    id = Column(Integer(), primary_key = True)
    text = Column(String(128), nullable = False, unique = True)

class Protocol(DeclarativeBase, ForeignValues):
    __tablename__ = 'protocols'

    id = Column(Integer(), primary_key = True)
    text = Column(String(32), nullable = False, unique = True)

class Domain(DeclarativeBase, ForeignValues):
    __tablename__ = 'domains'

    id = Column(Integer(), primary_key = True)
    text = Column(String(256), nullable = False, unique = True)

class ServerAddress(DeclarativeBase, ForeignValues):
    __tablename__ = 'server_address'

    id = Column(Integer(), primary_key = True)
    text = Column(String(256), nullable = False, unique = True)

#Squid AccessLog
#logformat expected:
# %ts %tr %>a %Ss %Hs %>st %<st %rm %un %ru %Sh %<A %mt 
class Access(DeclarativeBase):
    __tablename__ = 'access'
    
    id = Column(Integer(), primary_key = True)
    date = Column(Date(), nullable = False)
    time = Column(Time(), nullable = False)
    ms = Column(Integer(), nullable = False, default = 0)
    duration = Column(Integer(), nullable = False)

    address_id = Column(Integer(), ForeignKey('address.id'))
    address = relation(Address, backref = 'Access')

    proxy_status_id = Column(Integer(), ForeignKey('proxy_status.id'))
    proxy_status = relation(ProxyStatus, backref = 'Access')

    http_code = Column(Integer(), nullable = False)

    request_size = Column(Integer(), nullable = False)
    reply_size = Column(Integer(), nullable = False)

    method_id = Column(Integer(), ForeignKey('methods.id'))
    method = relation(Method, backref = 'Access')

    protocol_id = Column(Integer(), ForeignKey('protocols.id'))
    protocol = relation(Protocol, backref = 'Access')

    domain_id = Column(Integer(), ForeignKey('domains.id'))
    domain = relation(Domain, backref = 'Access')

    port = Column(Integer(), nullable = False)
    url_path = Column(String(512), nullable = True)

    proxy_user_id = Column(Integer(), ForeignKey('proxy_users.id'))
    proxy_user = relation(ProxyUser, backref = 'Access')

    hierarchy_status_id = Column(Integer(), ForeignKey('hierarchy_status.id'))
    hierarchy_status = relation(HierarchyStatus,
                        backref = 'Access')

    server_address_id = Column(Integer(), ForeignKey('server_address.id'))
    server_address = relation(ServerAddress, backref = 'Access')

    mime_type_id = Column(Integer(), ForeignKey('mime_types.id'))
    mime_type = relation(MimeType, backref = 'Access')

class MiniAccess(DeclarativeBase):
    __tablename__ = 'miniaccess'

    id = Column(Integer(), primary_key = True)
    date = Column(Date(), nullable = False)

    address_id = Column(Integer(), ForeignKey('address.id'))
    address = relation(Address, backref = 'MiniAccess')

    domain_id = Column(Integer(), ForeignKey('domains.id'))
    domain = relation(Domain, backref = 'Miniaccess')

    proxy_user_id = Column(Integer(), ForeignKey('proxy_users.id'))
    proxy_user = relation(ProxyUser, backref = 'MiniAccess')

    upload_bytes = Column(Integer(), nullable = False)
    download_bytes = Column(Integer(), nullable = False)

    count = Column(Integer(), nullable = False)

    #Status values:
    allowed = '0'
    denied = '1'
    status = Column(Integer(), nullable = False)

    @classmethod
    def update(mini_cls, access):
        proxy_status = access.proxy_status.text
        if proxy_status.startswith('UDP_') or proxy_status == 'NONE':
            return
        if access.proxy_status.text == 'TCP_DENIED':
            status = mini_cls.denied
        else:
            status = mini_cls.allowed

        mini = DBSession.query(mini_cls).\
                            join(Address).\
                            join(Domain).\
                            join(ProxyUser).\
                            filter(and_(Address.text == access.address.text,
                                    Domain.text == access.domain.text,
                                    ProxyUser.text == access.proxy_user.text,
                                    mini_cls.date == access.date,
                                    mini_cls.status == status)).all()
                                    
        if len(mini) == 0:
            mini = mini_cls()
            mini.date = access.date
            mini.address = access.address
            mini.domain = access.domain
            mini.proxy_user = access.proxy_user
            mini.upload_bytes = int(access.request_size)
            mini.download_bytes = int(access.reply_size)
            mini.count = 1
            mini.status = status
            DBSession.add(mini)
        else:
            mini = mini[0]
            mini.upload_bytes += int(access.request_size)
            mini.download_bytes += int(access.reply_size)
            mini.count += 1

