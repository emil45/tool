from mttkinter.mtTkinter import *
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt
import sendMessage
import threading


class stats_window():
    def __init__(self, win_name, parent):
        self.parent = parent
        self.parent.add_to_open_stats_win(win_name,self)
        self.winName = win_name
        self.host = (win_name.split(" -"))[0]

        self.root = Toplevel()
        self.root.resizable(width=False, height=False)
        self.root.title(self.winName)
        self.plt = plt

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, columnspan=3)

        self.pingFrame = Frame(self.root)
        self.pingFrame.grid(row=1, column=0)

        self.portFrame = Frame(self.root)
        self.portFrame.grid(row=1, column=1)

        self.commandFrame = Frame(self.root)
        self.commandFrame.grid(row=1, column=2)

        try:

            # create cpu graph
            self.cpu_fig = self.plt.figure(figsize=(10, 3), dpi=100)
            self.cpu_axl = self.cpu_fig.add_subplot(1, 1, 1)
            self.cpu_axl.set_title("cpu usage")
            self.cpu_axl.grid(True)
            self.cpu_axl.set_ylim([0, 100])
            cpu_x_list = ['']
            cpu_y_list = [0]
            self.plt.setp(self.cpu_axl.xaxis.get_majorticklabels(), rotation=80)
            self.cpuCanvas = FigureCanvasTkAgg(self.cpu_fig, self.frame)
            self.cpuCanvas.get_tk_widget().grid(row=0, column=0, columnspan=8)

            self.cpu_animation = animation.FuncAnimation(self.cpu_fig, self.get_cpu_val, fargs=(cpu_x_list, cpu_y_list),
                                                         interval=1000, blit=False)

            self.plt.subplots_adjust(bottom=0.3, hspace=1)

            # create ram graph
            self.ram_fig = self.plt.figure(figsize=(10, 3), dpi=100)
            self.ram_axl = self.ram_fig.add_subplot(1, 1, 1)
            self.ram_axl.set_title("memory usage")
            self.ram_axl.grid(True)
            self.ram_axl.set_ylim([0, 100])
            ram_x_list = ['']
            ram_y_list = [0]
            self.plt.setp(self.ram_axl.xaxis.get_majorticklabels(), rotation=80)
            self.ramCanvas = FigureCanvasTkAgg(self.ram_fig, self.frame)
            self.ramCanvas.get_tk_widget().grid(row=1, column=0, columnspan=8)
            self.ram_animation = animation.FuncAnimation(self.ram_fig, self.get_ram_val, fargs=(ram_x_list, ram_y_list),
                                                         interval=1000, blit=False)
            self.plt.subplots_adjust(bottom=0.3, hspace=1)

            # create ping check
            self.pingReq = Text(self.pingFrame, height=1, width=15)
            self.pingReq.grid(row=4,column=0)
            self.pingButton = Button(self.pingFrame, text="check ping availability", command=self.ping_ip_val)
            self.pingButton.grid(row=4, column=1)
            self.pingAnswer = Text(self.pingFrame, height=8, width=35)
            self.pingAnswer.grid(row=5, column=0, columnspan=2)
            self.pingAnswer.config(state=DISABLED)

            # create port transportation get
            self.portReq = Text(self.portFrame, height=1, width=15)
            self.portReq.grid(row=4, column=2)
            self.portButton = Button(self.portFrame, text="check port transportation", command=self.check_port_transportation)
            self.portButton.grid(row=4, column=3)
            self.portAnswer = Text(self.portFrame, height=8, width=35)
            self.portAnswer.grid(row=5, column=2, columnspan=2)
            self.portAnswer.config(state=DISABLED)

            # create command
            self.commandReq = Text(self.commandFrame, height=1, width=15)
            self.commandReq.grid(row=4, column=4)
            self.commandButton = Button(self.commandFrame, text="execute command", command=self.execute_command)
            self.commandButton.grid(row=4, column=5)
            self.commandAnswer = Text(self.commandFrame, height=8, width=35)
            self.commandAnswer.grid(row=5, column=4, columnspan=2) # sticky="nsew", padx=2, pady=2
            # command scrollbar
            self.commandAnswerScrollbar = Scrollbar(self.commandFrame, orient="vertical")
            self.commandAnswerScrollbar.grid(row=5, column=6, sticky="news")
            self.commandAnswerScrollbar.config(command=self.commandAnswer.yview)
            self.commandAnswer.config(state=DISABLED, yscrollcommand=self.commandAnswerScrollbar.set)

        except OSError as e:
            if sys.platform.startswith('win') and isinstance(e, WindowsError) and e.winerror == 10061:
                message_to_log = str.format("%s is unavailable" % self.host)
                self.parent.add_message_to_log(message_to_log)
                self.exit()
                pass

        # exit function
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.root.focus_force()


    def get_cpu_val(self, i, x_list, y_list):
        try:
            cpu_val = float(sendMessage.send_messages(self.host, 'cpu'))
        except OSError as e:
            if sys.platform.startswith('win') and isinstance(e, WindowsError) and e.winerror == 10061:
                message_to_log = str.format("%s is unavailable" % self.host)
                self.parent.add_message_to_log(message_to_log)
                self.exit()
                return
        except Exception as e:
            print ('invalid cpu val')
            message_to_log = str.format("%s is unavailable" % self.host)
            self.parent.add_message_to_log(message_to_log)
            self.exit()
            return

        y_list.append(cpu_val)
        x_list.append(dt.datetime.now().strftime('%H:%M:%S'))

        x_list = x_list[-60:]
        y_list = y_list[-60:]

        self.cpu_axl.set_xlim(x_list[0], x_list[-1])
        self.cpu_axl.fill_between(x_list, y_list, 0, facecolor='white')
        self.cpu_axl.fill_between(x_list, y_list, 0, facecolor='blue', alpha=0.1)
        self.cpu_axl.plot(x_list, y_list, color='blue')

    def get_ram_val(self, i, x_list, y_list):
        ram_val = sendMessage.send_messages(self.host, 'ram')

        if ram_val == "[WinError 10061] No connection could be made because the target machine actively refused it":
            self.exit()

        y_list.append(ram_val)
        x_list.append(dt.datetime.now().strftime('%H:%M:%S'))

        x_list = x_list[-60:]
        y_list = y_list[-60:]

        self.ram_axl.set_xlim(x_list[0], x_list[-1])
        self.ram_axl.fill_between(x_list, y_list, 0, facecolor='white')
        self.ram_axl.fill_between(x_list, y_list, 0, facecolor='purple', alpha=0.1)
        self.ram_axl.plot(x_list, y_list, color='purple')

    def ping_ip_val(self):
        ping_thread = threading.Thread(target=self.thread_ping_ip_val)
        ping_thread.start()

    def thread_ping_ip_val(self):
        self.pingAnswer.config({"background": "light yellow"})
        ip_to_ping = self.pingReq.get("1.0", END).rstrip()
        ping_answer = sendMessage.send_messages(self.host, 'ping', ip_to_ping)
        if ping_answer:
            ping_answer = "available"
        else:
            ping_answer = "unavailable"

        self.pingAnswer.config(state=NORMAL)
        self.pingAnswer.delete(1.0, END)
        self.pingAnswer.insert(END, ping_answer)
        self.pingAnswer.config(state=DISABLED)
        self.pingAnswer.config({"background": "white"})

    def check_port_transportation(self):
        port_thread = threading.Thread(target=self.thread_check_port_transportation)
        port_thread.start()

    def thread_check_port_transportation(self):
        self.portAnswer.config({"background": "light yellow"})
        port_to_check = self.portReq.get("1.0", END).rstrip()
        if not port_to_check.isdigit():
            port_answer = "unknown port"
        else:
            port_answer = sendMessage.send_messages(self.host, 'port', port_to_check)
            if port_answer:
                port_answer = "active port"
            else:
                port_answer = "unavailable port"

        self.portAnswer.config(state=NORMAL)
        self.portAnswer.delete(1.0, END)
        self.portAnswer.insert(END, port_answer)
        self.portAnswer.config(state=DISABLED)
        self.portAnswer.config({"background": "white"})

    def execute_command(self):
        commnd_thread = threading.Thread(target=self.thread_execute_command)
        commnd_thread.start()

    def thread_execute_command(self):
        self.commandAnswer.config({"background": "light yellow"})
        command_to_execute = self.commandReq.get("1.0", END).rstrip()
        command_answer = sendMessage.send_messages(self.host, 'command', command_to_execute)

        self.commandAnswer.config(state=NORMAL)
        self.commandAnswer.delete(1.0, END)
        self.commandAnswer.insert(END, command_answer)
        self.commandAnswer.config(state=DISABLED)
        self.commandAnswer.config({"background": "white"})

    def exit(self):
        message_to_log = str.format("%s stats window was closed" % self.winName)
        self.parent.add_message_to_log(message_to_log)
        self.parent.update_connection_list()
        try:
            try:
                self.pingReq.delete(0, END)
                self.portReq.delete(0, END)
                self.commandReq.delete(0, END)
            except Exception as e:
                if e == "'stats_window' object has no attribute 'pingReq'":
                    pass
            self.root.destroy()
            self.parent.remove_from_open_stats_win(self.winName)
        except Exception as e:
            print(e)
            print('cant close')
            pass

    def bring_to_front(self):
        self.root.tkraise()
        self.root.focus_force()



