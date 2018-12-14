import json
import os
import socket
import logging
import subprocess
import threading

import win32serviceutil
import win32service
import win32event
import servicemanager
import psutil

TCP_IP = '0.0.0.0'
TCP_PORT = 10000
BUFFER_SIZE = 1024

logging.basicConfig(filename=r'c:\code\tool\agent\1.log', filemode="w", level=logging.DEBUG)


class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ToolAgent"
    _svc_display_name_ = "Tool Agent Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.agent_running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((TCP_IP, TCP_PORT))

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.sock.close()
        self.agent_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        logging.info("Service is started")
        self.sock.listen(5)
        while self.agent_running:
            monitor, address = self.sock.accept()
            monitor.settimeout(5)
            threading.Thread(target=self.receive_monitor_message, args=(monitor, address)).start()

    def ping(self, hostname):
        response = os.system(f"ping -c 1 -n 1 {hostname}")
        if response == 0:
            return True
        else:
            return False

    def run_command(self, command):
        return subprocess.Popen(command, stdout=subprocess.PIPE).stdout.read()

    def is_port_free(self, port):
        return len(subprocess.Popen(f'netstat -na | findstr "\<0.0.0.0:{port}\>"',
                                    shell=True, stdout=subprocess.PIPE).stdout.read()) > 0

    def analyze_monitor_message(self, binary_monitor_request):
        monitor_request = json.loads(binary_monitor_request)
        if "cpu" in monitor_request:
            monitor_request["cpu"] = psutil.cpu_percent()
        if "ram" in monitor_request:
            monitor_request["ram"] = psutil.virtual_memory().percent
        if "ping" in monitor_request:
            hostname = monitor_request["ping"]
            monitor_request["ping"] = self.ping(hostname)
        if "port" in monitor_request:
            port = monitor_request["port"]
            monitor_request["port"] = self.is_port_free(port)
        if "command" in monitor_request:
            command = monitor_request["command"]
            monitor_request["command"] = self.run_command(command)
        binary_monitor_answer = json.dumps(monitor_request).encode()
        return binary_monitor_answer

    def receive_monitor_message(self, monitor, address):
        logging.debug(f'Connection information: {address}')
        while True:
            try:
                monitor_request = monitor.recv(BUFFER_SIZE).decode()
                if monitor_request:
                    logging.debug(f"Received monitor request: {monitor_request}")
                    monitor_answer = self.analyze_monitor_message(monitor_request)
                    logging.debug(f"Sending monitor answer: {monitor_answer}")
                    monitor.send(monitor_answer)
            except Exception as ex:
                logging.error(ex)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
