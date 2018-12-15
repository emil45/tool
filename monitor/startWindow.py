from mttkinter import mtTkinter
import findIpsOnNetwork
import statsWindow
import threading
import datetime as dt

class StartWindow:
    def __init__(self):
        print('search all ips on network')

        self.root = mtTkinter.Tk()
        self.root.title('available IP\'s')
        self.root.resizable(width=False, height=False)

        self.frame = mtTkinter.Frame(self.root, relief=mtTkinter.FLAT, bd=1)
        self.frame.grid(row=0, column=0, padx=2, pady=2, sticky=mtTkinter.N + mtTkinter.W + mtTkinter.E)
        self.frame.columnconfigure(0, weight=1)

        self.listbox = mtTkinter.Listbox(self.frame, width=100, height=15)
        self.listbox.grid(row=1,column=0, sticky="ew", padx=2, pady=2)
        # listbox scrollbar
        self.listboxScrollbar = mtTkinter.Scrollbar(self.frame, orient="vertical")
        self.listboxScrollbar.grid(row=1, column=1, padx=2,pady=2,sticky="ns")
        self.listboxScrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.listboxScrollbar.set)

        #create log textbox
        self.log = mtTkinter.Text(self.frame, height=15, width=100)
        self.log.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.log.config(state=mtTkinter.DISABLED)
        # log scrollbar
        self.logScrollbar = mtTkinter.Scrollbar(self.frame, orient="vertical")
        self.logScrollbar.grid(row=2, column=1, padx=2, pady=2, sticky="ns")
        self.logScrollbar.config(command=self.log.yview)
        self.log.config(yscrollcommand=self.logScrollbar.set)

        # update list button
        self.commandButton = mtTkinter.Button(self.frame, text="update connections list", command=self.update_connection_list)
        self.commandButton.grid(row=3, column=0, sticky="ew")

        self.openStatsWin = {}

        self.update_connection_list()
        self.log.delete("1.0", mtTkinter.END)

        self.listbox.bind("<Double-Button-1>", self.clicked_on_ip)

        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.root.mainloop()

    def update_connection_list(self):

        self.listbox.delete(0, mtTkinter.END)

        ip_list = findIpsOnNetwork.find_network_ips(self)
        if len(ip_list) == 0:
            self.add_message_to_log("no agents found")

        for item in ip_list:
            self.listbox.insert(mtTkinter.END, item)

        self.add_message_to_log("updated connected ip list")

    def exit(self):
        print('close main win')
        keys_list = list(self.openStatsWin.keys())
        for key in keys_list:
            try:
                self.openStatsWin[key].root.quit()
            except Exception as e:
                print(e)
                print('cant quit from main')
                self.openStatsWin[key].exit()
        self.root.destroy()

    def add_message_to_log(self, message):
        msg = str.format('%s - %s \n' % (dt.datetime.now().strftime('%d.%m.%y %H:%M:%S'), message))
        self.log.config(state=mtTkinter.NORMAL)
        self.log.insert(mtTkinter.END, msg)
        self.log.config(state=mtTkinter.DISABLED)


    def remove_from_open_stats_win(self, host_var):
        del self.openStatsWin[host_var]

    def add_to_open_stats_win(self, host_var, stats_win):
        self.openStatsWin[host_var] = stats_win

    def open_stats_win(self, host_var):
        statsWindow.stats_window(host_var, self)

    def clicked_on_ip(self, event):
        index = self.listbox.curselection()[0]
        win_name = self.listbox.get(index)
        if win_name not in self.openStatsWin:
            stats_thread = threading.Thread(target=self.open_stats_win, args=(win_name,))
            stats_thread.start()
        else:
            msg = str.format('%s stats window already open' % win_name)
            self.add_message_to_log(msg)
            self.openStatsWin[win_name].bring_to_front()


