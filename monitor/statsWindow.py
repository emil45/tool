from mttkinter.mtTkinter import *
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt
import sendMessage
import threading


class stats_window():
    def __init__(self, win_name, parent):

        self.lock = threading.Lock()
        self.parent = parent
        self.parent.add_to_open_stats_win(win_name,self)
        self.winName = win_name
        self.host = (win_name.split(" -"))[0]

        self.root = Toplevel()
        self.root.resizable(width=False, height=False)
        self.root.title(self.winName)
        self.plt = plt

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0)

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
            self.pingReq = Text(self.frame, height=1, width=15)
            self.pingReq.grid(row=4,column=0)
            self.pingButton = Button(self.frame, text="check ping availability", command=self.ping_ip_val)
            self.pingButton.grid(row=4, column=1)
            self.pingAnswer = Text(self.frame, height=8, width=35)
            self.pingAnswer.grid(row=5, column=0, columnspan=2)
            self.pingAnswer.config(state=DISABLED)

            # create port transportation get
            self.portReq = Text(self.frame, height=1, width=15)
            self.portReq.grid(row=4, column=2)
            self.portButton = Button(self.frame, text="check port transportation", command=self.check_port_transportation)
            self.portButton.grid(row=4, column=3)
            self.portAnswer = Text(self.frame, height=8, width=35)
            self.portAnswer.grid(row=5, column=2, columnspan=2)
            self.portAnswer.config(state=DISABLED)

            # create command
            self.commandReq = Text(self.frame, height=1, width=15)
            self.commandReq.grid(row=4, column=4)
            self.commandButton = Button(self.frame, text="execute command", command=self.execute_command)
            self.commandButton.grid(row=4, column=5)
            self.commandAnswer = Text(self.frame, height=8, width=35)
            self.commandAnswer.grid(row=5, column=4, columnspan=2, sticky="nsew", padx=2, pady=2)
            # command scrollbar
            self.commandAnswerScrollbar = Scrollbar(self.commandAnswer, orient="vertical")
            self.commandAnswerScrollbar.pack(side=RIGHT, fill=Y)
            self.commandAnswerScrollbar.config(command=self.commandAnswer.yview)
            self.commandAnswer.config(state=DISABLED, yscrollcommand=self.commandAnswerScrollbar.set)

        except OSError as e:
            if sys.platform.startswith('win') and isinstance(e, WindowsError) and e.winerror == 10061:
                message_to_log = str.format("%s is unavailable" % self.host)
                self.parent.add_message_to_log(message_to_log)
                self.exit()
                self.lock.release()
                pass

        # exit function
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.root.focus_force()

    def get_cpu_val(self, i, x_list, y_list):
        self.lock.acquire()
        try:
            cpu_val = float(sendMessage.send_messages(self.host, 'cpu'))
        except OSError as e:
            print ('invalid cpu val - %s' % cpu_val)
            if sys.platform.startswith('win') and isinstance(e, WindowsError) and e.winerror == 10061:
                message_to_log = str.format("%s is unavailable" % self.host)
                self.parent.add_message_to_log(message_to_log)
                self.lock.release()
                self.exit()
                pass
        except Exception as e:
            print ('invalid cpu val')
            message_to_log = str.format("%s is unavailable" % self.host)
            self.parent.add_message_to_log(message_to_log)
            self.lock.release()
            self.exit()
            pass
        self.lock.release()

        y_list.append(cpu_val)
        x_list.append(dt.datetime.now().strftime('%H:%M:%S'))

        x_list = x_list[-60:]
        y_list = y_list[-60:]

        self.cpu_axl.set_xlim(x_list[0], x_list[-1])
        self.cpu_axl.fill_between(x_list, y_list, 0, facecolor='white')
        self.cpu_axl.fill_between(x_list, y_list, 0, facecolor='blue', alpha=0.1)
        self.cpu_axl.plot(x_list, y_list, color='blue')

    def get_ram_val(self, i, x_list, y_list):
        self.lock.acquire()
        ram_val = sendMessage.send_messages(self.host, 'ram')
        self.lock.release()

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
        ip_to_ping = self.pingReq.get("1.0", END).rstrip()

        self.lock.acquire()
        ping_answer = sendMessage.send_messages(self.host, 'ping', ip_to_ping)
        self.lock.release()

        self.pingAnswer.config(state=NORMAL)
        self.pingAnswer.delete(1.0, END)
        self.pingAnswer.insert(END, ping_answer)
        self.pingAnswer.config(state=DISABLED)
        self.pingAnswer.config({"background": "light cyan"})
        self.root.after(350, self.change_color, self.pingAnswer)

    def check_port_transportation(self):
        port_to_check = self.portReq.get("1.0", END).rstrip()

        self.lock.acquire()
        port_answer = sendMessage.send_messages(self.host, 'port', port_to_check)
        self.lock.release()

        self.portAnswer.config(state=NORMAL)
        self.portAnswer.delete(1.0, END)
        self.portAnswer.insert(END, port_answer)
        self.portAnswer.config(state=DISABLED)
        self.portAnswer.config({"background": "light cyan"})
        self.root.after(350, self.change_color, self.portAnswer)

    def execute_command(self):
        command_to_execute = self.commandReq.get("1.0", END).rstrip()

        self.lock.acquire()
        command_answer = sendMessage.send_messages(self.host, 'command', command_to_execute)
        self.lock.release()

        self.commandAnswer.config(state=NORMAL)
        self.commandAnswer.delete(1.0, END)
        self.commandAnswer.insert(END, command_answer)
        self.commandAnswer.config(state=DISABLED)
        self.commandAnswer.config({"background": "light cyan"})
        self.root.after(350, self.change_color, self.commandAnswer)

    @staticmethod
    def change_color(text_box):
        text_box.config({"background": "white"})

    def exit(self):
        message_to_log = str.format("%s stats window was closed" % self.winName)
        self.parent.add_message_to_log(message_to_log)
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



