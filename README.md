# Vultriever - Vulnerability scoring with NmapVultriever - a small tool that allows you to convert to Excel and JSON formats the results of using the Nmap scanner in conjunction with the built-in Vulners snap-in. It was created to automate the process of inventory of open ports and running network services on the server and scoring of existing vulnerabilities determined based on the versions of the software used. Implemented the use of Vultriever from the terminal and as an imported module in native Python scripts. Vultriever usage in TERMINAL:Specific IP-address:    sudo python vultriever.py [ip_address] [Nmap argument] [Nmap argument] ... [Nmap argument]    sudo python vultriever.py x.x.x.x O sV Pn                        List of IP-addresses:     sudo python vultriever.py [filename].txt [Nmap argument] [Nmap argument] ... [Nmap argument]    sudo python vultriever.py list.txt O sV PnThe format of the list is a column of IP-addresses line by line without spaces and other characters:    x.x.x.x    y.y.y.y        .......        z.z.z.z                               Vultriever usage in PYTHON CODE:    vultriever.py(<ip_address>,[ [Nmap argument], [Nmap argument], ..., [Nmap argument] ])    ----------------- PYTHON SCRIPT -----------------                                from vultriever import vultriever        result = vultriever('x.x.x.x', ['O','sV','Pn'])                                -------------------------------------------------vultriever() function works for one IP-address in time and returns information in JSON format with next structure:    {        "ip_address" : "x.x.x.x",        "ports" : [                                    {                            "number" : 26,                            "status" : "open",                            "protocol" : "smtp",                            "service" : "Eximsmtpd4.95",                            "vulnerabilities" : [                                                                                    {                                                        "cve" : "CVE-2022-37452",                                                        "score" : "9.8",                                                        "url" : "https://vulners.com/cve/CVE-2022-37452"                                                    }                                                            ]                                                    }                    ]    }Incorrect request will result to 'error_message' in JSON response keys                            {                "error_message" : <error message>            }