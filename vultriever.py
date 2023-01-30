# coding: utf-8

import re
import os
import sys
import subprocess
import openpyxl
import json

servers_pattern = re.compile('Nmap scan report for .+(?:\n[\S| |\t]+)+')
server_pattern = re.compile('\d+\.\d+\.\d+\.\d+')
ip_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
ports_pattern = re.compile('\d+/[open|close|filtered][\S| |\t]+\n(?:\|[\S| |\t]+\n)*')
port_pattern = re.compile('\d+')
CVE_pattern = re.compile('\|[ |\t]+CVE-\d+-\d+[\t]+\d.\d[\t]+\S+')

command_patterns = [
                        '--help',
                        '\d+\.\d+\.\d+\.\d+$',
                        '\d+\.\d+\.\d+\.\d+(?:\s[-0-9a-zA-Z]+)+',
                        '\S+\.txt$',
                        '\S+\.txt(?:\s[-0-9a-zA-Z]+)+'
                    ]

logo = """        
                                                                            
    ██╗   ██╗██╗   ██╗██╗  ████████╗██████╗ ██╗███████╗██╗   ██╗███████╗██████╗ 
    ██║   ██║██║   ██║██║  ╚══██╔══╝██╔══██╗██║██╔════╝██║   ██║██╔════╝██╔══██╗
    ██║   ██║██║   ██║██║     ██║   ██████╔╝██║█████╗  ██║   ██║█████╗  ██████╔╝
    ╚██╗ ██╔╝██║   ██║██║     ██║   ██╔══██╗██║██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗
     ╚████╔╝ ╚██████╔╝███████╗██║   ██║  ██║██║███████╗ ╚████╔╝ ███████╗██║  ██║
      ╚═══╝   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝

                   IN MEMORY OF VINCENT. DEFENDER, HUNTER & FRIEND                             

⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⢿⣿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⢁⣤⣶⣶⣶⣶⣿⣿⣿⣷⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣤⣉⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⢀⢴⣾⣿⠏⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠻⣷⣄⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⡀⣡⣿⠿⠃⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣌⢈⠻⣷⣄⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⢂⠜⡩⠴⠀⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣛⢿⣿⣿⣿⣿⣿⣦⠡⠙⢿⣿⣦⡈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⣰⣿⣿⠏⢠⡡⢠⣿⣿⣿⡿⠛⠉⢉⠉⠛⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⡀⠀⠉⢙⠿⣿⣿⣿⣧⠡⠁⠹⣿⣷⣄⡈⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠿⠟⢃⣠⣾⡿⢋⡜⠀⣸⢃⣾⣿⣿⠏⠀⠀⠐⠀⠀⠄⠘⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇⢀⠀⠀⠂⠈⠐⡙⢿⣿⣿⡄⣧⠀⠈⠻⣿⣿⡂⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⡦⠉⣴⣶⣿⣿⠿⣋⣴⣿⠀⢰⠃⣸⣿⣿⣷⡄⢀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡈⢀⣀⠀⠀⠤⣶⣾⣿⣷⡀⡈⠁⠀⣷⣌⡻⣿⣦⣁⠀⠀⠿⣿⣿⣿⣿⣿
⣿⣿⣿⡿⠃⢠⣿⣿⡿⣿⣿⣿⣿⡇⠀⡟⠀⣿⣿⣿⣿⣿⣷⣿⣿⡟⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣌⢻⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀⣿⡟⢿⣷⣝⠿⣷⡀⠈⠙⠿⣿⣿⣿
⣿⣿⣿⠟⠠⣿⡿⣋⣴⢟⣿⡟⣹⣿⠀⡇⢰⣿⣿⣿⣿⣿⣿⣿⠟⣰⣿⣿⣿⣿⡿⠿⠛⠛⠛⠛⠻⢿⣿⣿⣿⣿⣦⠹⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⣿⣿⣦⡝⢌⢳⣌⠃⠀⠓⢶⣿⣿⣿
⣿⣿⢏⠀⢠⣿⡿⣫⣴⡿⢋⣴⣿⣿⠀⡇⢸⣿⣿⣿⣿⡿⠿⣋⣼⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣧⣘⠿⣿⣿⣿⣿⣿⡿⠀⠀⡇⣿⣿⡝⣿⣦⡙⢷⠀⡈⢿⣿⣿⣿
⣿⣿⣁⡀⠈⢫⣾⡿⢋⣴⣾⣿⡿⠛⠀⠇⢸⣿⡟⣋⣭⣴⣾⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣷⣬⣍⡛⢿⣿⡇⠀⠀⡇⣿⣯⠹⣌⠻⣿⣬⠀⢻⣿⣿⣿⣿
⣿⣿⣿⡆⠀⠘⣩⣾⡿⢋⣼⡿⢁⣦⠈⠀⢸⣿⠰⣿⡈⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⡿⢿⡜⣿⠁⠀⣰⢰⣿⣿⣑⠹⣧⡘⡿⠀⠈⣿⣿⣿⣿
⣿⣿⣿⣷⠀⠸⠛⣉⡴⢋⢟⠁⣾⣿⠀⠀⢸⣿⣧⣿⠁⠙⣿⣿⣿⣿⣿⣿⣿⣷⣤⣄⡀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⡿⠋⠀⡹⡇⣿⠀⠀⠃⣿⣟⠻⣝⠳⣠⠱⠆⠀⠀⣿⣿⣿⣿
⣿⣿⣿⣿⡄⠀⢠⣿⠔⡡⣢⣾⣿⣿⠃⠆⠘⡿⢿⣿⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⣙⣻⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⢠⢠⣿⡏⠀⢰⠀⣿⣿⡀⢌⠻⡟⠁⣀⢀⣠⣿⣿⣿⣿
⣿⣿⣿⣿⣷⣦⠀⠠⠾⢿⣿⠿⠟⡛⢠⠀⢰⣣⢛⣿⡼⡄⠀⠈⠻⢿⣿⣿⣿⣟⠿⠟⢃⡀⢀⠙⠯⠻⢿⣿⣿⣟⣛⠋⢠⠀⢀⢇⣿⣿⠁⠀⢸⢦⠹⣷⡙⠧⠑⠀⣄⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣶⡄⠀⡀⣡⠦⠀⡠⠁⠀⠸⡟⢸⣿⣇⢸⡄⠈⢶⣤⣤⠀⣤⣤⣶⣶⣿⡇⢸⣿⣶⣶⣤⡄⠀⠀⣠⣶⣿⠁⢸⣿⣿⡟⠀⠀⠘⡟⢢⢸⡇⢠⡀⣼⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡆⠡⡀⠀⠟⠁⠀⠀⠀⠀⡾⣿⣿⣆⠳⠄⢠⣿⡆⠀⢻⣿⣿⣿⣿⡇⣿⣿⣿⣿⡿⠀⡄⢰⣿⣿⠄⢀⣿⣿⢯⣇⠀⠀⠀⢿⣆⠘⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⡤⠖⠀⣆⣄⡀⡸⢃⣿⣿⣿⣆⢰⡀⢻⣷⠀⢸⣿⣿⣿⣿⣧⣿⣿⣿⣿⡇⠐⢀⣿⣿⠏⠀⣾⠻⢿⠀⢻⣦⣷⡀⠀⠙⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢰⡇⢸⣿⣏⢁⢡⡾⠙⣿⣿⣿⡘⠷⡈⢻⣦⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢠⣾⣿⠋⠀⣼⣿⠎⠈⢀⢸⣿⢸⡇⠹⣆⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⢸⡇⢸⣿⣿⣸⢸⠇⢐⣿⣿⣿⣷⡄⢿⣄⠻⣇⠈⢿⣿⣿⣿⣿⣿⣿⠋⢠⡿⠛⠁⢀⣼⣿⣾⣆⣴⠘⣿⣿⣾⡿⢠⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠘⡃⢸⣿⣿⣿⡜⢠⠟⠏⢼⣿⣿⣿⣎⢻⣦⠙⢧⡀⠙⠻⠿⠿⠟⢁⡴⠋⠀⠀⣠⣿⠿⣿⡇⣿⣿⣤⣾⣿⡿⠁⢸⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠃⢈⢿⣿⣿⡇⠈⡤⠀⠸⢹⣿⣿⣿⣧⣙⠳⣄⠉⠓⠶⣶⣶⠿⠋⠀⣀⣠⣪⣾⡟⡄⢠⠀⢩⣿⣿⣿⣿⢃⣶⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡘⡎⠈⣿⣿⣿⣾⠀⡆⣴⠀⣼⣿⣿⣿⣿⣷⣬⡃⢄⠐⠒⠒⠀⡠⢞⣫⣽⣿⣿⣿⠁⠀⠀⢸⣿⣿⣿⡟⢸⢷⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⢰⡀⠸⣿⣿⣿⣤⡀⠏⠀⠁⢹⣿⣿⣿⡿⣿⣿⣷⣾⣭⣭⣭⣶⣿⣿⣿⣟⣿⣥⠀⣄⠙⣿⣿⣿⡿⢠⡟⠈⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠓⣄⢹⣿⣿⣿⣇⣠⣁⣿⠈⡃⠹⣿⣷⢸⠏⡀⠛⣿⣿⠿⡿⣿⣿⠏⠀⣺⡟⡀⢹⣾⣿⣿⡿⢡⡿⡐⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠘⢯⣿⣿⣿⣿⣿⠃⠋⡀⣼⣿⣿⠙⠈⣰⡕⠀⠻⢁⠀⠀⣿⢃⣔⣰⠏⣰⣿⣿⣿⣿⣿⢡⣿⠐⣱⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⠻⣿⣿⣿⣿⣿⣿⣷⣿⣿⣷⣷⣾⣿⣾⠀⠰⣿⠀⠡⣸⣿⡿⣁⣾⣿⣿⣽⣿⣿⣷⠟⣡⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣬⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⣴⣧⣿⣧⣶⣿⣋⣴⣿⣿⣿⣿⣿⣿⣿⣋⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿

OFFICIAL SITE:          www.malwarehunters.org
TELEGRAM CHANNEL:       t.me/malwarehunters
TELEGRAM CONTACT:       t.me/malware_hunters
TWITTER:                twitter.com/@_malwarehunters
EMAIL:                  threat@malwarehunters.org

⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
"""

help_message = """
VULTRIEVER usage in TERMINAL:

Specific IP-address:    # sudo python vultriever.py <ip_address> <Nmap argument> <Nmap argument> ... <Nmap argument>
                        # sudo python vultriever.py x.x.x.x O sV Pn
                        
List of IP-addresses:   # sudo python vultriever.py <filename>.txt <Nmap argument> <Nmap argument> ... <Nmap argument>
                        # sudo python vultriever.py list.txt O sV Pn

                        The format of the list is a column of IP-addresses line by line without spaces and other characters:
                        
                         -------
                        |x.x.x.x|
                        |y.y.y.y|
                        |       |
                        |.......|
                        |       |
                        |z.z.z.z|
                         -------
                         
VULTRIEVER usage in PYTHON CODE:    

                        vultriever(<ip_address>,[<Nmap argument>, <Nmap argument>, ..., <Nmap argument>])

                        ----------------- PYTHON SCRIPT -----------------
                        
                        from vultriever import vultriever

                        result = vultriever('x.x.x.x', ['O','sV','Pn'])
                        
                        -------------------------------------------------

                        vultriever() function works for one IP-address in time and 
                        returns information in JSON format with next structure:

                        {
                            "ip_address" : "x.x.x.x",
                            "ports" : [
                                
                                            {
                                                "number" : 26,
                                                "status" : "open",
                                                "protocol" : "smtp",
                                                "service" : "Eximsmtpd4.95",
                                                "vulnerabilities" : [
                                                    
                                                                        {
                                                                            "cve" : "CVE-2022-37452",
                                                                            "score" : "9.8",
                                                                            "url" : "https://vulners.com/cve/CVE-2022-37452"
                                                                        }
                                                    
                                                ]
                                                
                                            }
                                
                            ]
                        }

                        Incorrect request will result to 'error_message' in JSON response keys
                        
                        {
                            
                            "error_message" : <error message>
                            
                        }

                        """

class NMap_Collector(object):
    
    nmap_info = []
    
    def __init__(self, nmap_result):
    
        servers_info = re.findall(servers_pattern, nmap_result)
        for server_info in servers_info:
        
            temp_info = {}
        
            server = re.findall(server_pattern, server_info)[0]
            temp_info.update({
                                "ip_address": server, 
                                "ports": []
                            })
            
            ports_info = re.findall(ports_pattern, server_info)
            for port_info in ports_info:

                port = re.findall(port_pattern, port_info)[0]
                port_status = list(filter(None, port_info.split('\n')[0].split(' ')))
                CVEs_info = re.findall(CVE_pattern, port_info)
                
                vulnerabilities = []
                if CVEs_info:

                    for CVE_info in CVEs_info:
                    
                        info = CVE_info.split('\t')                
                        vulnerabilities.append({
    
                                                    "cve": info[1],
                                                    "score": info[2],
                                                    "url": info[3]
    
                                                })

                temp_info["ports"].append({
                                                "number": port,
                                                "status": port_status[1] if len(port_status) >= 2 else '',
                                                "protocol": port_status[2] if len(port_status) >= 3 else '',
                                                "service": ' '.join(port_status[3:]) if len(port_status) >= 4 else '',
                                                "vulnerabilities": vulnerabilities
                                            })
                                            
                                                                        
            self.nmap_info.append(temp_info)


def vultriever(ip_address_func=None, nmap_args_func=None):
    
    def args_check(args):
        
        msg = None
        ip_addresses = []
        nmap_args = []

        args_string = " ".join(args)

        for command_pattern in command_patterns:
            
            command = re.findall(re.compile(command_pattern), args_string)

            if command:

                if len(command[0]) == len(args_string):

                    if '.txt' in args_string:

                        with open(args[0],'r') as ips_list:

                            for ip_address in ips_list.readlines():
                            
                                if re.match(re.compile(ip_pattern), ip_address.strip()):
                            
                                    ip_addresses.append(ip_address.strip())
                                    nmap_args = args[1:]
                                    
                                else:
                                
                                    msg = "Incorrect IP-address: {0}".format(ip_address.strip())
                                    break

                        break

                    elif '--help' in args_string:
                    
                        msg = help_message
                    
                    else:

                        if re.match(re.compile(ip_pattern), args[0].strip()):

                            ip_addresses = [args[0]]
                            nmap_args = args[1:]
                            break
                            
                        else:
                        
                            msg = "Incorrect IP-address: {0}".format(args[0].strip())
                            break
                            
        return msg, ip_addresses, nmap_args

    try:
    
        if ip_address_func or nmap_args_func: msg, ip_addresses, nmap_args = args_check([ip_address_func]+nmap_args_func)
        else: msg, ip_addresses, nmap_args = args_check(sys.argv[1:])
    
        if not msg:
        
            if not ip_address_func and not nmap_args_func: 
            
                os.system('clear')
                print(logo)
            
            ### NMAP
            
            nmap_args_string = ''
    
            if nmap_args: 
            
                for arg in nmap_args:
                    
                    if arg.isdigit(): nmap_args_string += ' '+str(arg)
                    else: nmap_args_string += ' -'+arg
    
            with open('nmap_result.txt', 'w') as log:
    
                if not ip_address_func and not nmap_args_func: 
                
                    for ip_address in ip_addresses: 
        
                        if nmap_args_string: nmap_command = "nmap{0} --script vulners {1}".format(nmap_args_string, ip_address)
                        else: nmap_command = "nmap --script vulners {0}".format(ip_address)
            
                        try:
    
                            print('\nUsing command: ' + nmap_command)
                            nmap_process = subprocess.call(nmap_command, shell=True, stdout=log)
                            print('{0} scanning has finished ...'.format(ip_address))
        
                        except Exception as error: 
                            
                            print(error)
                            return 0                
                
                    print('Write information to file ...\n')
    
                else:
            
                    for ip_address in ip_addresses: 
        
                        if nmap_args_string: nmap_command = "nmap{0} --script vulners {1}".format(nmap_args_string, ip_address)
                        else: nmap_command = "nmap --script vulners {0}".format(ip_address)
            
                        try:
                                
                            nmap_process = subprocess.call(nmap_command, shell=True, stdout=log)
        
                        except Exception as error: 
                            
                            return json.dumps({'error_message': str(error)})
    
            ### RESPONSE
    
            with open('nmap_result.txt', 'r') as nmap_result:
    
                if ip_address_func or nmap_args_func:
                
                    ### JSON
                
                    try:
    
                        nmap_collector = NMap_Collector(nmap_result.read())
                        return json.dumps(nmap_collector.nmap_info[0])
                        
                    except Exception as error:
                    
                        return json.dumps({'error_message':str(error)})
                
                else:
    
                    ### EXCEL
        
                    excel_book = openpyxl.Workbook()
                    del excel_book['Sheet']
                    excel_sheet = excel_book.create_sheet('CVE Info')
                    excel_sheet.cell(row=1,column=1,value='IP')
                    excel_sheet.cell(row=1,column=2,value='Port')
                    excel_sheet.cell(row=1,column=3,value='Status')
                    excel_sheet.cell(row=1,column=4,value='Protocol')
                    excel_sheet.cell(row=1,column=5,value='Service')
                    excel_sheet.cell(row=1,column=6,value='CVE')
                    excel_sheet.cell(row=1,column=7,value='Score')
                    excel_sheet.cell(row=1,column=8,value='URL')
        
                    row_num = 2
                        
                    nmap_collector = NMap_Collector(nmap_result.read())
                                            
                    for nmap_server_info in nmap_collector.nmap_info:
                    
                        for nmap_port_info in nmap_server_info.get("ports"):
                    
                            if nmap_port_info.get("vulnerabilities"):
                            
                                for nmap_port_vuln_info in nmap_port_info.get("vulnerabilities"):
                            
                                    excel_sheet.cell(row=row_num,column=1,value=nmap_server_info.get("ip_address"))
                                    excel_sheet.cell(row=row_num,column=2,value=nmap_port_info.get("number"))
                                    excel_sheet.cell(row=row_num,column=3,value=nmap_port_info.get("status"))
                                    excel_sheet.cell(row=row_num,column=4,value=nmap_port_info.get("protocol"))
                                    excel_sheet.cell(row=row_num,column=5,value=nmap_port_info.get("service"))
                                    excel_sheet.cell(row=row_num,column=6,value=nmap_port_vuln_info.get("cve"))
                                    excel_sheet.cell(row=row_num,column=7,value=nmap_port_vuln_info.get("score"))
                                    excel_sheet.cell(row=row_num,column=8,value=nmap_port_vuln_info.get("url"))
                                    row_num += 1
                            
                            else:
                                                
                                excel_sheet.cell(row=row_num,column=1,value=nmap_server_info.get("ip_address"))
                                excel_sheet.cell(row=row_num,column=2,value=nmap_port_info.get("number"))
                                excel_sheet.cell(row=row_num,column=3,value=nmap_port_info.get("status"))
                                excel_sheet.cell(row=row_num,column=4,value=nmap_port_info.get("protocol"))
                                excel_sheet.cell(row=row_num,column=5,value=nmap_port_info.get("service"))
                                row_num += 1
                
                    print('Done!')
                    excel_book.save('Vultriever.xlsx')
            
        else: 
        
            if not ip_address_func and not nmap_args_func: 
    
                os.system('clear')
                print(logo)
                print(msg)
                
            else: return json.dumps({'error_message':msg})
        
    except Exception as error: print(error)

if __name__ == '__main__':

    vultriever()