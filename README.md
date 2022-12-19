# Vultriever - Vulnerability scoring with NmapVultriever - a small tool that allows you to convert to Excel and JSON formats the results of using the Nmap scanner in conjunction with the built-in Vulners snap-in. It was created to automate the process of inventory of open ports and running network services on the server and scoring of existing vulnerabilities determined based on the versions of the software used. Implemented the use of Vultriever from the terminal and as an imported module in native Python scripts. In the process, Vultriever collects and provides the following information about the server in a structured form:<ul><li>Server IP address</li><li>Network port number</li><li>Network port status</li><li>Protocol used by the network port</li><li>Network service operating on the network port and its version</li><li>Vulnerability CVE-identifier</li><li>Vulnerability rating</li><li>URL-link to the description of the vulnerability on the platform Vulners.com</li></ul>## Vultriever usage in TERMINAL:In this mode, Vultriever returns the result in Excel document format.Analysis of specific IP-address:    sudo python vultriever.py <ip_address> <Nmap argument> <Nmap argument> ... <Nmap argument>    sudo python vultriever.py x.x.x.x O sV Pn<img src="terminal.png">                        Analysis of list of IP-addresses:     sudo python vultriever.py <filename>.txt <Nmap argument> <Nmap argument> ... <Nmap argument>    sudo python vultriever.py list.txt O sV PnThe format of the list is a column of IP-addresses line by line without spaces and other characters:    x.x.x.x    y.y.y.y        .......        z.z.z.z                        Result Excel document:<img src="excel.png">    ## Vultriever usage in PYTHON code:In this mode, Vultriever returns the result in JSON format.    vultriever(<ip_address>, [<Nmap argument>, <Nmap argument>, ..., <Nmap argument>])Python Script    from vultriever import vultriever        result = vultriever('x.x.x.x', ['O','sV','Pn'])vultriever() function works for one IP-address in time and returns information in JSON format with next structure:    {        "ip_address" : "x.x.x.x",        "ports" : [                                    {                            "number" : 26,                            "status" : "open",                            "protocol" : "smtp",                            "service" : "Eximsmtpd4.95",                            "vulnerabilities" : [                                                                                    {                                                        "cve" : "CVE-2022-37452",                                                        "score" : "9.8",                                                        "url" : "https://vulners.com/cve/CVE-2022-37452"                                                    }                                                            ]                                                    }                    ]    }Incorrect request will result to 'error_message' in JSON response keys                            {                "error_message" : <error message>            }    ## Requirements<ul><li>Nmap</li><li>openpyxl python module</li></ul>