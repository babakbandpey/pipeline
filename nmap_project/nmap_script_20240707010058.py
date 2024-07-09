import nmap
nm = nmap.PortScanner()
ip_addresses = ['172.28.128.1', '192.168.56.1']
for ip in ip_addresses:
    nm.scan(ip)
    print(f'Scan results for {ip}:')
    print(nm[ip])
