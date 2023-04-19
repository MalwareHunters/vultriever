# coding: utf-8

import os
import socket
import json
import re

from ipwhois import IPWhois
import whois
from ISO3166 import ISO3166

def ip_resolver(ip):

    ip_info = {
        'ip':ip,
        'country':'',
        'city':'',
        'provider':'',
        'asn': ''
    }

    country = ''
    city = ''
    provider = ''
    asn = ''
    
    ip_substr = re.findall(r'\d+\.\d+\.\d+\.\d+', ip)

    if ip_substr:
    
        try: 

            info = IPWhois(ip).lookup_whois()
    
            if ISO3166.get(info.get('nets')[0]['country']): country = ISO3166.get(info.get('nets')[0]['country'])
            if info.get('nets')[0]['city']: city = info.get('nets')[0]['city']
            if info.get('nets')[0]['description']: provider = info.get('nets')[0]['description']
            if 'asn' in info: asn = info.get('asn').split(' ')[0]
    
            if not country or not city or not provider: raise Exception('IPWhois.lookup_whois not found full information')
    
        except Exception as err: pass
    
        try:
    
            info = IPWhois(ip).lookup_rdap(asn_methods=['dns','whois','http'])
    
            if not country and ISO3166.get(info.get('asn_country_code')): country = ISO3166.get(info.get('asn_country_code'))
            if not provider: 
                for key in info.get('objects').keys():
                    if 'registrant' in info.get('objects').get(key).get('roles'): 
                        provider = info.get('objects').get(key).get('contact').get('name')
                        break
            if not asn and 'asn' in info: asn = info.get('asn').split(' ')[0]
    
            if not country or not city: raise Exception('IPWhois.lookup_rdap not found full information')
    
        except Exception as err: pass
        
    ip_info['country'] = country
    ip_info['city'] = city
    ip_info['provider'] = provider
    ip_info['asn'] = asn
    
    return ip_info

def domain_resolver(domain):

    domain_info = {
        'domain':domain,
        'registrar':'',
        'servers': []
    }

    domain = str(domain.split('/')[0])
    
    ip_string = r'\d+\.\d+\.\d+\.\d+'
    ip_substr = re.findall(ip_string, domain)

    if ip_substr:

        uniq_ips = [ip_substr[0]]

    else:
    
        try:
            domain_info['registrar'] = whois.query(domain).__dict__.get('registrar')
        except Exception as err: pass

        uniq_ips = []
        try:
            socket.setdefaulttimeout(10)
            resolver_ips = socket.getaddrinfo(domain, None)
            uniq_ips = [itm for itm in set(ip[4][0] for ip in resolver_ips)]
        except Exception as err: 
            uniq_ips = []

    if uniq_ips:
        for ip in uniq_ips: domain_info['servers'].append(ip_resolver(ip))

    return domain_info    




