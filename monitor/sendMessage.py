import socket
import json
import sys
import configparser


def ts(s, message, func):
    s.send(message.encode())
    #s.settimeout(0.2)
    data = s.recv(1024).decode()
    j = json.loads(data)
    return j[func]

def create_message(func, params):
    j = json.dumps({func:params})
    return j


def send_messages(host, func, params='True'):
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        port = int(config['DEFAULT']['PORT'])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        m = create_message(func, params)
        return ts(s, m, func)
        s.close()
    except OSError as e:
        if sys.platform.startswith('win'):
            if isinstance(e, WindowsError) and e.winerror == 10061:
                raise e
    except Exception as e:
        print (e)
        return "error detected"