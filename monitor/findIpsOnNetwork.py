from socket import *
import configparser


def is_up(addr, port, monitor):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(0.1)    # set a timeout of 0.1 sec
    try:
        if not s.connect((addr, port)):
            s.close()
            return 1
        else:
            s.close()
    except Exception as e:
        error_string = str.format("%s ocured while trying to access %s:%s" % (e,addr,port))
        monitor.add_message_to_log(error_string)
        pass


def find_network_ips(monitor):
    config = configparser.ConfigParser()
    config.read('config.ini')
    ip_config_list = config['DEFAULT']['IP_LIST'].split(", ")
    port = int(config['DEFAULT']['PORT'])
    ip_list = []
    for ip in ip_config_list:
        if is_up(ip, port, monitor):
            ip_host = str.format('%s - %s' % (ip, getfqdn(ip)))
            ip_list.append(ip_host)
    return ip_list
