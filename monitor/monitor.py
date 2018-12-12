import socket
import json
import sys


def ts(s, message, func):
    s.send(message.encode())
    data = s.recv(1024).decode()
    j = json.loads(data)
    return j[func]

def create_message(func, params):
    j = json.dumps({func:params})
    return j


def send_messages(host, func, params='True'):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 10000
        s.connect((host, port))
        m = create_message(func, params)
        return ts(s, m, func)
        s.close()
    except OSError as e:
        if sys.platform.startswith('win'):
            if isinstance(e, WindowsError) and e.winerror == 10061:
                raise e
    except Exception as e:
        return "error detected"