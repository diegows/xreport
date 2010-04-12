# -*- coding: utf-8 -*-
"""Fallback controller."""

from tg import expose, flash, require, url, request, redirect, validate, config
from tg import session
from pylons import c
from tw.jquery import FlexiGrid
from formencode import validators
from sqlalchemy import func, and_, desc, asc
from sqlalchemy.sql.expression import case, literal_column
from datetime import datetime

from squid.model import DBSession, MiniAccess, Address, Domain, ProxyUser
from squid.lib.base import BaseController
from squid.lib.misc import link

__all__ = ['ReportsController']

main_report_cols = [
    { 'display' : 'Date', 'name' : 'date', 'width' : '200', 
        'align' : 'center' },
    { 'display' : 'Clients', 'name' : 'clients', 'width' : '60', 
        'align' : 'center' },
    { 'display' : 'Users', 'name' : 'users', 'width' : '60', 
        'align' : 'center' },
    { 'display' : 'Sites', 'name' : 'sites', 'width' : '60', 
        'align' : 'center' },
    { 'display' : 'Requests', 'name' : 'requests', 'width' : '80', 
        'align' : 'center' },
    { 'display' : 'Download (MB)', 'name' : 'download_bytes', 'width' : '120', 
        'align' : 'center' },
    { 'display' : 'Upload (MB)', 'name' : 'upload_bytes', 'width' : '120', 
        'align' : 'center' } ]


main_report_grid = FlexiGrid(id = 'main_report',
                fetchURL = url('/reports/fetch_main_report'),
                title = 'Main proxy report',
                sortname = 'date',
                sortorder = 'desc', usepager = True,
                howTableToggleButton = True,
                colModel = main_report_cols,
                width = 900,
                height = 300)

clients_report_cols = [
    { 'display' : 'Address', 'name' : 'address', 'width' : '100', 
        'align' : 'center' },
    { 'display' : 'Sites', 'name' : 'sites', 'width' : '60', 
        'align' : 'center' },
    { 'display' : 'Requests', 'name' : 'requests', 'width' : '80', 
        'align' : 'center' },
    { 'display' : 'Download (MB)', 'name' : 'download_bytes', 'width' : '120', 
        'align' : 'center' },
    { 'display' : 'Upload (MB)', 'name' : 'upload_bytes', 'width' : '120', 
        'align' : 'center' } ]

clients_report_grid = FlexiGrid(id = 'clients_report',
                fetchURL = url('/reports/fetch_clients_report'),
                title = 'Clients proxy report',
                sortname = 'download_bytes',
                sortorder = 'desc', usepager = True,
                howTableToggleButton = True,
                colModel = clients_report_cols,
                width = 900,
                height = 300)

users_report_cols = [
    { 'display' : 'Username', 'name' : 'proxy_user', 'width' : '100', 
        'align' : 'center' },
    { 'display' : 'Sites', 'name' : 'sites', 'width' : '60', 
        'align' : 'center' },
    { 'display' : 'Requests', 'name' : 'requests', 'width' : '80', 
        'align' : 'center' },
    { 'display' : 'Download (MB)', 'name' : 'download_bytes', 'width' : '120', 
        'align' : 'center' },
    { 'display' : 'Upload (MB)', 'name' : 'upload_bytes', 'width' : '120', 
        'align' : 'center' } ]

users_report_grid = FlexiGrid(id = 'users_report',
                fetchURL = url('/reports/fetch_users_report'),
                title = 'User proxy report',
                sortname = 'download_bytes',
                sortorder = 'desc', usepager = True,
                howTableToggleButton = True,
                colModel = users_report_cols,
                width = 900,
                height = 300)

sites_report_cols = [
    { 'display' : 'Site', 'name' : 'sites', 'width' : '210', 
        'align' : 'center' },
    { 'display' : 'Address', 'name' : 'address', 'width' : '60', 
        'align' : 'center' },
    { 'display' : 'Users', 'name' : 'proxy_user', 'width' : '50', 
        'align' : 'center' },
    { 'display' : 'Requests', 'name' : 'requests', 'width' : '80', 
        'align' : 'center' },
    { 'display' : 'Download (MB)', 'name' : 'download_bytes', 'width' : '105', 
        'align' : 'center' },
    { 'display' : 'Upload (MB)', 'name' : 'upload_bytes', 'width' : '105', 
        'align' : 'center' } ]

sites_report_grid = FlexiGrid(id = 'sites_report',
                fetchURL = url('/reports/fetch_sites_report'),
                title = 'Sites proxy report',
                sortname = 'download_bytes',
                sortorder = 'desc', usepager = True,
                howTableToggleButton = True,
                colModel = sites_report_cols,
                width = 900,
                height = 300)
 
userip_sites_report_cols = [
    { 'display' : 'Site', 'name' : 'address', 'width' : '280', 
        'align' : 'center' },
    { 'display' : 'Requests', 'name' : 'requests', 'width' : '80', 
        'align' : 'center' },
    { 'display' : 'Download (MB)', 'name' : 'download_bytes', 'width' : '105', 
        'align' : 'center' },
    { 'display' : 'Upload (MB)', 'name' : 'upload_bytes', 'width' : '105', 
        'align' : 'center' } ]

userip_sites_report_grid = FlexiGrid(id = 'userip_sites_report',
                fetchURL = url('/reports/fetch_userip_sites_report'),
                title = 'Per User/IP sites proxy report',
                sortname = 'download_bytes',
                sortorder = 'desc', usepager = True,
                howTableToggleButton = True,
                colModel = userip_sites_report_cols,
                width = 900,
                height = 300)

sites_userip_report_cols = [
    { 'display' : 'User/IP', 'name' : 'address', 'width' : '210', 
        'align' : 'center' },
    { 'display' : 'Requests', 'name' : 'requests', 'width' : '80', 
        'align' : 'center' },
    { 'display' : 'Download (MB)', 'name' : 'download_bytes', 'width' : '105', 
        'align' : 'center' },
    { 'display' : 'Upload (MB)', 'name' : 'upload_bytes', 'width' : '105', 
        'align' : 'center' } ]

sites_userip_report_grid = FlexiGrid(id = 'sites_userip_report',
                fetchURL = url('/reports/fetch_sites_userip_report'),
                title = 'User/IP sites proxy report',
                sortname = 'download_bytes',
                sortorder = 'desc', usepager = True,
                howTableToggleButton = True,
                colModel = sites_userip_report_cols,
                width = 900,
                height = 300)


def get_sortfn(sortorder):
    if sortorder == 'desc':
        return desc
    else:
        return asc

def mb(bytes):
    return '%.02f' % float(float(bytes)/1038336)

class ReportsController(BaseController):
    @expose('squid.templates.reports')
    def index(self):
        session['group_by'] = 'day'
        session.save()
        c.reports = main_report_grid
        return dict()

    @expose('squid.templates.reports')
    def week(self):
        session['group_by'] = 'week'
        session.save()
        c.reports = main_report_grid
        return dict()

    @expose('squid.templates.reports')
    def month(self):
        session['group_by'] = 'month'
        session.save()
        c.reports = main_report_grid
        return dict()
    
    @expose('squid.templates.reports')
    def clients(self, *kw):
        session['date'] = kw[0]
        session.save()
        c.reports = clients_report_grid
        c.query_params = { 'Date' : session['date'] }
        c.backlink = '/reports/reports'
        return dict(page = 'squid')

    @expose('squid.templates.reports')
    def users(self, *kw):
        session['date'] = kw[0]
        session.save()
        c.reports = users_report_grid
        c.query_params = { 'Date' : session['date'] }
        c.backlink = '/reports/reports'
        return dict(page = 'squid')

    @expose('squid.templates.reports')
    def sites(self, *kw):
        session['date'] = kw[0]
        session.save()
        c.reports = sites_report_grid
        c.query_params = { 'Date' : session['date'] }
        c.backlink = '/reports/reports'
        return dict(page = 'squid')

    @expose('squid.templates.reports')
    def ip_sites(self, *kw):
        session['func'] = 'ip_sites'
        session['ip'] = kw[0]
        session.save()
        c.reports = userip_sites_report_grid
        c.query_params = { 'Date' : session['date'],
                            'IP' : session['ip'] }
        c.backlink = '/reports/clients/' + session['date']
        return dict(page = 'squid')
 
    @expose('squid.templates.reports')
    def user_sites(self, *kw):
        session['func'] = 'user_sites'
        session['user'] = kw[0]
        session.save()
        c.reports = userip_sites_report_grid
        c.query_params = { 'Date' : session['date'],
                            'User' : session['user'] }
        c.backlink = '/reports/users/' + session['date']
        return dict(page = 'squid')

    @expose('squid.templates.reports')
    def sites_ip(self, *kw):
        session['func'] = 'sites_ip'
        session['site'] = kw[0]
        session.save()
        site = DBSession.query(Domain).get(session['site'])
        c.reports = sites_userip_report_grid
        c.query_params = { 'Date' : session['date'],
                            'Site' : site.text }
        c.backlink = '/reports/sites/' + session['date']
        return dict(page = 'squid')

    @validate(validators={ "page" : validators.Int(), "rp" : validators.Int()})
    @expose('json')
    def fetch_main_report(self, page = 1, rp = 25, sortname = 'date',
                    sortorder = 'desc', qtype = None, query = None):

        dash_id = DBSession.query(ProxyUser.id).filter(ProxyUser.text == "-")
        dash_id = dash_id.one()[0]

        count_ip = """count(distinct if(miniaccess.proxy_user_id = %d,
            miniaccess.address_id, 0))""" % (dash_id)

        count_user = """count(distinct if(miniaccess.proxy_user_id <> %d,
            miniaccess.proxy_user_id, 0))""" % (dash_id)

        if session['group_by'] == 'day':
            date_col = MiniAccess.date
        else:
            date_col = func.concat(func.min(MiniAccess.date), ' - ', 
                            func.max(MiniAccess.date))
                   
        #count the clients address only if the request is not authenticated
        #I use literal SQL because i don't find how to do this with ORM.
        main = DBSession.query(date_col,
                                count_ip,
                                count_user,
                                func.count(MiniAccess.domain_id.distinct()),
                                func.sum(MiniAccess.count),
                                func.sum(MiniAccess.download_bytes),
                                func.sum(MiniAccess.upload_bytes))
        main = main.group_by(MiniAccess.date)

        sort_fn = get_sortfn(sortorder)
        if sortname == 'date':
            main = main.order_by(sort_fn(MiniAccess.date))
        elif sortname == 'clients':
            main = main.order_by(sort_fn('2'))
        elif sortname == 'users':
            main = main.order_by(sort_fn('3'))
        elif sortname == 'sites':
            main = main.order_by(sort_fn('count_1'))
        elif sortname == 'requests':
            main = main.order_by(sort_fn('sum_1'))
        elif sortname == 'download_bytes':
            main = main.order_by(sort_fn('sum_2'))
        elif sortname == 'upload_bytes':
            main = main.order_by(sort_fn('sum_3'))

        total = main.count()
        offset = (page - 1) * rp
        main = main.offset(offset).limit(rp)

        rows = []
        print main
        for data in main:
            urldate = data[0]
            clients = link('reports/clients', urldate, data[1])
            # We don't count '-' user because it's used in unauth. msgs.
            users = link('reports/users', urldate, data[2])
            sites = link('reports/sites', urldate, data[3])
            values = [ data[0], clients, users, sites, data[4],
                        mb(data[5]),
                        mb(data[6]) ]
            row = { 'id' : data[0],
                    'cell' : values }
            rows.append(row)

        return dict(page = page, total = total, rows = rows)

    @validate(validators={ "page" : validators.Int(), "rp" : validators.Int()})
    @expose('json')
    def fetch_clients_report(self, page = 1, rp = 25,
                    sortname = 'download_bytes', sortorder = 'desc',
                    qtype = None, query = None):

        clients = DBSession.query(Address.text,
                                func.count(MiniAccess.domain_id.distinct()),
                                func.sum(MiniAccess.count),
                                func.sum(MiniAccess.download_bytes),
                                func.sum(MiniAccess.upload_bytes))
        clients = clients.join(MiniAccess, ProxyUser)
        clients = clients.group_by(Address.text)

        clients = clients.filter(and_(MiniAccess.date == session['date'],
                                        ProxyUser.text == '-'))
        
        sort_fn = get_sortfn(sortorder)
        if sortname == 'sites':
            clients = clients.order_by(sort_fn('count_1'))
        elif sortname == 'requests':
            clients = clients.order_by(sort_fn('sum_1'))
        elif sortname == 'download_bytes':
            clients = clients.order_by(sort_fn('sum_2'))
        elif sortname == 'upload_bytes':
            clients = clients.order_by(sort_fn('sum_3'))

        total = clients.count()
        offset = (page - 1) * rp
        clients = clients.offset(offset).limit(rp)

        rows = []
        for data in clients:
            sites = link('reports/ip_sites', data[0], data[1])
            values = [ data[0], sites, data[2],
                        mb(data[3]),
                        mb(data[4]) ]
            row = { 'id' : data[0],
                    'cell' : values }
            rows.append(row)

        return dict(page = page, total = total, rows = rows)

    @validate(validators={ "page" : validators.Int(), "rp" : validators.Int()})
    @expose('json')
    def fetch_users_report(self, page = 1, rp = 25,
                    sortname = 'download_bytes', sortorder = 'desc',
                    qtype = None, query = None):

        clients = DBSession.query(ProxyUser.text,
                                func.count(MiniAccess.domain_id.distinct()),
                                func.sum(MiniAccess.count),
                                func.sum(MiniAccess.download_bytes),
                                func.sum(MiniAccess.upload_bytes))
        clients = clients.join(MiniAccess)
        clients = clients.group_by(ProxyUser.text)

        clients = clients.filter(and_(MiniAccess.date == session['date'],
                                        ProxyUser.text != '-'))
        
        sort_fn = get_sortfn(sortorder)
        if sortname == 'sites':
            clients = clients.order_by(sort_fn('count_1'))
        elif sortname == 'requests':
            clients = clients.order_by(sort_fn('sum_1'))
        elif sortname == 'download_bytes':
            clients = clients.order_by(sort_fn('sum_2'))
        elif sortname == 'upload_bytes':
            clients = clients.order_by(sort_fn('sum_3'))

        total = clients.count()
        offset = (page - 1) * rp
        clients = clients.offset(offset).limit(rp)

        rows = []
        for data in clients:
            sites = link('reports/user_sites', data[0], data[1])
            values = [ data[0], sites, data[2],
                        mb(data[3]),
                        mb(data[4]) ]
            row = { 'id' : data[0],
                    'cell' : values }
            rows.append(row)

        return dict(page = page, total = total, rows = rows)

    @validate(validators={ "page" : validators.Int(), "rp" : validators.Int()})
    @expose('json')
    def fetch_sites_report(self, page = 1, rp = 25,
                    sortname = 'download_bytes', sortorder = 'desc',
                    qtype = None, query = None):

        clients = DBSession.query(Domain.text,
                                func.count(MiniAccess.address_id.distinct()),
                                func.count(MiniAccess.proxy_user_id.distinct()),
                                func.sum(MiniAccess.count),
                                func.sum(MiniAccess.download_bytes),
                                func.sum(MiniAccess.upload_bytes),
                                Domain.id)
        clients = clients.join(MiniAccess)
        clients = clients.group_by(Domain.text)

        clients = clients.filter(MiniAccess.date == session['date'])
        
        sort_fn = get_sortfn(sortorder)
        if sortname == 'address':
            clients = clients.order_by(sort_fn('count_1'))
        elif sortname == 'proxy_user':
            clients = clients.order_by(sort_fn('count_2'))
        elif sortname == 'requests':
            clients = clients.order_by(sort_fn('sum_1'))
        elif sortname == 'download_bytes':
            clients = clients.order_by(sort_fn('sum_2'))
        elif sortname == 'upload_bytes':
            clients = clients.order_by(sort_fn('sum_3'))

        total = clients.count()
        offset = (page - 1) * rp
        clients = clients.offset(offset).limit(rp)

        rows = []
        for data in clients:
            clients = link("reports/sites_ip", data[6], data[1])
            users = link("reports/sites_users", data[6], int(data[2]) - 1)
            values = [ data[0], clients, users, data[3],
                        mb(data[4]),
                        mb(data[5]) ]
            row = { 'id' : data[0],
                    'cell' : values }
            rows.append(row)

        return dict(page = page, total = total, rows = rows)

    @validate(validators={ "page" : validators.Int(), "rp" : validators.Int()})
    @expose('json')
    def fetch_userip_sites_report(self, page = 1, rp = 25,
                    sortname = 'download_bytes', sortorder = 'desc',
                    qtype = None, query = None):

        clients = DBSession.query(Domain.text,
                                func.sum(MiniAccess.count),
                                func.sum(MiniAccess.download_bytes),
                                func.sum(MiniAccess.upload_bytes))

        if session['func'] == 'ip_sites':
            filter = Address.text == session['ip']
            clients = clients.join(MiniAccess, Address)
        else:
            filter = ProxyUser.text == session['user']
            clients = clients.join(MiniAccess, ProxyUser)

        clients = clients.group_by(Domain.text)
        date = datetime.strptime(session['date'], '%Y-%m-%d')
        date = date.date()
        clients = clients.filter(and_(MiniAccess.date == date, filter))
        
        sort_fn = get_sortfn(sortorder)
        if sortname == 'requests':
            clients = clients.order_by(sort_fn('sum_1'))
        elif sortname == 'download_bytes':
            clients = clients.order_by(sort_fn('sum_2'))
        elif sortname == 'upload_bytes':
            clients = clients.order_by(sort_fn('sum_3'))

        total = clients.count()
        offset = (page - 1) * rp
        clients = clients.offset(offset).limit(rp)

        rows = []
        for data in clients:
            values = [ data[0], data[1],
                        mb(data[2]),
                        mb(data[3]) ]
            row = { 'id' : data[0],
                    'cell' : values }
            rows.append(row)

        return dict(page = page, total = total, rows = rows)

    @validate(validators={ "page" : validators.Int(), "rp" : validators.Int()})
    @expose('json')
    def fetch_sites_userip_report(self, page = 1, rp = 25,
                    sortname = 'download_bytes', sortorder = 'desc',
                    qtype = None, query = None):

        if session['func'] == 'sites_ip':
            userip = Address.text
        else:
            userip = ProxyUser.text

        clients = DBSession.query(userip,
                                func.sum(MiniAccess.count),
                                func.sum(MiniAccess.download_bytes),
                                func.sum(MiniAccess.upload_bytes))

        if session['func'] == 'sites_ip':
            clients = clients.join(MiniAccess.address)
            clients = clients.group_by(MiniAccess.address_id)
        else:
            clients = clients.join(MiniAccess.proxy_user)
            clients = clients.group_by(MiniAccess.proxy_user_id)

        clients = clients.join(MiniAccess.domain)
        date = datetime.strptime(session['date'], '%Y-%m-%d')
        date = date.date()
        clients = clients.filter(and_(MiniAccess.date == date, 
                                    MiniAccess.domain_id == session['site']))
        
        sort_fn = get_sortfn(sortorder)
        if sortname == 'requests':
            clients = clients.order_by(sort_fn('sum_1'))
        elif sortname == 'download_bytes':
            clients = clients.order_by(sort_fn('sum_2'))
        elif sortname == 'upload_bytes':
            clients = clients.order_by(sort_fn('sum_3'))

        total = clients.count()
        offset = (page - 1) * rp
        clients = clients.offset(offset).limit(rp)

        rows = []
        for data in clients:
            values = [ data[0], data[1],
                        mb(data[2]),
                        mb(data[3]) ]
            row = { 'id' : data[0],
                    'cell' : values }
            rows.append(row)

        return dict(page = page, total = total, rows = rows)

