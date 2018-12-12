from socket import *


def is_up(addr, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(0.2)    # set a timeout of 0.2 sec
    try:
        if not s.connect((addr, port)):
            s.close()
            return 1
        else:
            s.close()
    except:
        pass


def find_network_ips(start=1, end=256):
    local_host = gethostname()
    local_network_list = gethostbyname(local_host).split(".")
    local_network = "%s.%s.%s." % (local_network_list[0], local_network_list[1], local_network_list[2])
    port = 10000
    ip_list = []
    for ip in range(start, end):
        addr = local_network + str(ip)
        if is_up(addr, port):
            ip_host = str.format('%s - %s' % (addr, getfqdn(addr)))
            ip_list.append(ip_host)
    return ip_list
