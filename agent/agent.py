import random
import time
from pathlib import Path

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "ToolAgent"
    _svc_display_name_ = "Tool Agent Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        while True:
            random.seed()
            x = random.randint(1, 1000000)
            Path(f'c:\\code\\tool\\test\\{x}.txt').touch()
            time.sleep(2)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
