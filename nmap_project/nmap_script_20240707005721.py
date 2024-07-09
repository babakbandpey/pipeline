import nmap
nm = nmap.PortScanner()
nm.scan('172.28.128.1 192.168.56.1')
print(nm.all_hosts())
