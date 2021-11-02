from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageChops
import psutil
import time
import threading
import ctypes
from Procs import Processes
from Misc import get_icon, search_all_vals, search_vals, get_list, page_icon
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class GUI_class:
    def __init__(self, width, height):
        self.gridroot = tk.Tk()
        self.height = height
        self.width = width
        self.lb_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
        self.process_list = []
        self.a_process_list = {}
        self.a_page_list = {}
        self.tab_list = []
        self.mon_procs = []
        self.mon_sites = []
        self.dup_proc_names = set()
        self.icons = []
        self.user32 = ctypes.windll.user32
        self.create_buttons()
        self.create_listboxes()
        self.welcome_screen()
        self.total_site_time = 0
        self.total_app_time = 0
        self.top_apps = {}
        self.top_sites = {}

    def mainloop(self):
        self.gridroot.mainloop()

    def add_to_proc_lb2(self, name, idx):
        self.Lb2.insert(idx, name)

    def add_to_proc_lb4(self, name):
        self.Lb4.insert(END, name)

    def del_selections(self):
        self.icon_tree.delete(self.icon_tree.focus())

    def del_selections_2(self):
        cur = self.Lb2.curselection()
        if not cur:
            return

        for s in cur:
            self.Lb2.delete(s)

    def del_selections_sites(self):
        self.icon_tree2.delete(self.icon_tree.focus())

    def del_selections_sites2(self):
        cur = self.Lb4.curselection()
        if not cur:
            return

        for s in cur:
            self.Lb4.delete(s)

    def rem_monitor_sels(self):
        cur = self.Lb2.curselection()
        if not cur:
            return

        for s in cur:
            name = self.Lb2.get(s)
            for i in enumerate(self.process_list[:]):
                if name == i.name:
                    self.process_list.remove(i)

    def rem_monitor_sels_sites(self):
        cur = self.Lb4.curselection()
        if not cur:
            return

        for s in cur:
            name = self.Lb4.get(s)
            for i in enumerate(self.mon_sites[:]):
                if name == i:
                    self.mon_sites.remove(i)

    def all_children(self, window):
        _list = window.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        return _list

    def create_canvas(self):
        img = Image.open('../assets/bg.jpg')
        img.resize((1300, 1000))
        background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.gridroot, image=background_image)
        background_label.photo = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def welcome_screen(self):
        self.gridroot.geometry(str(self.width + 'x' + self.height))
        self.time_text = Text(self.gridroot, font=self.lb_font, height=5, padx=5, pady=5, width=20, bd=1, relief='sunken')
        self.watchlist_btn.grid(column=0, row=0)
        self.main_title.grid(column=0, row=1)
        self.time_text.grid(column=2, row=6)
        self.setup_time_info()

    def select_tree_item(self, event):
        cur_item = self.icon_tree.focus()
        t = self.icon_tree.item(cur_item, "values")
        return t[0]

    def select_tree_item2(self, event):
        cur_item = self.icon_tree2.focus()
        t = self.icon_tree2.item(cur_item, "values")
        return t[0]

    def ret_tree_item(self):
        cur_item = self.icon_tree.focus()
        t = self.icon_tree.item(cur_item, "values")
        return t[0]

    def ret_tree_item2(self):
        cur_item = self.icon_tree2.focus()
        t = self.icon_tree2.item(cur_item, "values")
        return t[0]

    def add_to_monitor_list(self):
        name = self.ret_tree_item()
        pid = Processes.find_procname(name)
        self.mon_procs.append(name)
        self.add_to_proc_lb2(name, pid)

    def add_to_monitor_site_list(self):
        name = self.ret_tree_item2()
        self.mon_procs.append(name)
        self.add_to_proc_lb4(name)

    def setup_time_info(self):
        self.time_text.insert(INSERT, "--")
        self.time_text.insert(INSERT, "--")
        self.time_text.insert(INSERT, "--")
        self.time_text.insert(INSERT, "--")

    def display_time_info(self):
        try:
            self.time_text.delete('1.0', END)
            cur = self.Lb2.curselection()
            name = self.Lb2.get(cur)
            vals = search_vals(name, "apps")
            self.time_text.insert(INSERT, str("Seconds:" + str(vals[0]) + '\n'))
            self.time_text.insert(INSERT, str("Minutes:" + str(vals[1]) + '\n'))
            self.time_text.insert(INSERT, str("Hours:" + str(vals[2]) + '\n'))
            self.time_text.insert(INSERT, str("Weeks:" + str(vals[3]) + '\n'))
            self.create_graphics(name, "apps")
        except:
            print("You must add your selection to the watchlist first!")

    def display_site_time(self):
        try:
            self.time_text.delete('1.0', END)
            cur = self.Lb4.curselection()
            name = self.Lb4.get(cur)
            vals = search_vals(name, "sites")
            self.time_text.insert(INSERT, str("Seconds:" + str(vals[0]) + '\n'))
            self.time_text.insert(INSERT, str("Minutes:" + str(vals[1]) + '\n'))
            self.time_text.insert(INSERT, str("Hours:" + str(vals[2]) + '\n'))
            self.time_text.insert(INSERT, str("Weeks:" + str(vals[3]) + '\n'))
            self.create_graphics(name, "sites")
        except:
            print("You must add your selection to the watchlist first!")

    def create_graphics(self, name, Type):
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)

        sizes = []
        labels = []

        if Type == "sites":
            cur = self.a_page_list[name]
            items = self.top_sites.items()
            sizes = [cur, self.total_site_time - cur, list(items)[0][1], list(items)[1][1],
                     list(items)[2][1], list(items)[3][1], list(items)[4][1]]
            labels = name, "All other apps", list(items)[0][0], list(items)[1][0], \
                     list(items)[2][0], list(items)[3][0], list(items)[4][0]
        else:
            cur = self.a_process_list[name]
            items = self.top_apps.items()
            sizes = [cur, self.total_app_time - cur, list(items)[0][1], list(items)[1][1],
                     list(items)[2][1], list(items)[3][1], list(items)[4][1]]
            labels = name, "All other apps", list(items)[0][0], list(items)[1][0], \
                     list(items)[2][0], list(items)[3][0], list(items)[4][0]

        explode = (0.2, 0, 0, 0, 0, 0, 0)
        a.pie(sizes, explode=explode, labels=labels,
              shadow=True)

        canvas = FigureCanvasTkAgg(f, master=self.gridroot)
        canvas.draw()
        canvas.get_tk_widget().grid(row=4, column=1)

    def add_process(self, idx, name, pid, exe, didx):
        i = get_icon(exe)

        if i is None:
            return

        im = ImageTk.PhotoImage(i)
        self.icons.append(im)
        self.icon_tree.insert(parent='', index='end', image=im, values=(str(name)))

        self.process_list.append(name)
        process = self.create_process(name, pid, exe)

        num = search_vals(name, "apps")
        num = num[0] + num[1] + num[2] + num[3]

        self.a_process_list[name] = num
        self.calc_top_times("apps")
        return 1

    def create_process(self, info, pid, exe):
        return Processes(info, pid, exe)

    def update_proc_listbox(self):
        didx = 0
        for idx, proc in enumerate(psutil.process_iter(attrs=['pid', 'name', 'exe'])):
            with proc.oneshot():
                pid = proc.pid
                name = proc.name()

            po = psutil.Process(pid)

            with po.oneshot():
                parent = po.parent()

            if name in self.process_list:
                continue

            # adds process only if the name is not duplicated and that it's not a windows process
            if not Processes.rem_windows_procs(pid, name):
                exe = proc.exe()
                if parent is None:
                    if self.add_process(idx, name, pid, exe, didx) is not None:
                        didx += 1
                elif parent.name() == "explorer.exe":
                    if self.add_process(idx, name, pid, exe, didx) is not None:
                        didx += 1

    def update_page_listbox(self):
        for idx, page in enumerate(get_list("sites")):
            if str(page[0]) in self.a_page_list.values():
                continue

            name = str(page[0])
            imdata = str(page[1])
            num = search_vals(name, "sites")
            num = num[0] + num[1] + num[2] + num[3]

            page_icon(imdata)
            img = Image.open('../assets/picon.png')
            img = ImageTk.PhotoImage(img)

            self.icon_tree2.insert(parent='', index='end', image=img, values=(str(name)))
            self.a_page_list[name] = num
            self.total_site_time += num
            self.calc_top_times("sites")

    def calc_top_times(self, Type):
        all = {}
        for num in search_all_vals(Type):
            val = num[0] + num[1] + num[2] + num[3]
            name = num[4]
            all[name] = val

        a = dict(sorted(all.items(), key=lambda item: item[1]))

        if Type == "sites":
            self.top_sites = a
        else:
            self.top_apps = a


    def create_buttons(self):
        self.create_canvas()

        self.main_title = tk.Message(text="The monitor 9000", bg="#3E3432", fg="blue")

        self.watchlist_btn = tk.Button(self.gridroot, text='Program watchlist', bg='#3E3432', fg='#FB6F14',
                                  command=lambda: [self.monitor_apps_screen()])

        self.add_monitor_btn = tk.Button(self.gridroot, text='Add to monitor list', bg='#3E3432', fg='#FB6F14',
                                    command=lambda: [self.add_to_monitor_list(), self.del_selections()])

        self.add_monitor_site_btn = tk.Button(self.gridroot, text='Add to monitor list', bg='#3E3432', fg='#FB6F14',
                                         command=lambda: [self.add_to_monitor_site_list(), self.del_selections_sites()])

        self.rm_from_list_btn = tk.Button(self.gridroot, text='Remove from monitor list', bg='#3E3432', fg='#FB6F14',
                                    command=lambda: [self.rem_monitor_sels(), self.del_selections_2()])

        self.rm_from_site_list_btn = tk.Button(self.gridroot, text='Remove from monitor list', bg='#3E3432', fg='#FB6F14',
                                          command=lambda: [self.rem_monitor_sels_sites(), self.del_selections_sites2()])

        self.refresh_list_btn = tk.Button(self.gridroot, text='Refresh program list', bg='#3E3432', fg='#FB6F14',
                                     command=lambda: [threading.Thread(target=self.update_proc_listbox())])

        self.refresh_page_list_btn = tk.Button(self.gridroot, text='Refresh webpage list', bg='#3E3432', fg='#FB6F14',
                                           command=lambda: [self.update_page_listbox()])

        self.switch_apps_btn = tk.Button(self.gridroot, text='Switch to apps page', bg='#3E3432', fg='#FB6F14',
                                    command=lambda: [self.monitor_apps_screen()])

        self.switch_sites_btn = tk.Button(self.gridroot, text='Switch to sites page', bg='#3E3432', fg='#FB6F14',
                                     command=lambda: [self.monitor_sites_screen()])

        self.update_time_graphics_apps = tk.Button(self.gridroot, text='Get info for this', bg='#3E3432', fg='#FB6F14',
                                     command=lambda: [self.display_time_info()])

        self.update_time_graphics_sites = tk.Button(self.gridroot, text='Get info for this', bg='#3E3432', fg='#FB6F14',
                                                   command=lambda: [self.display_site_time()])

    def create_listboxes(self):
        self.Lb2 = tk.Listbox(self.gridroot, font=self.lb_font, selectmode=SINGLE, height=15, width=30)
        self.Lb2.bind()
        self.Lb4 = tk.Listbox(self.gridroot, font=self.lb_font, selectmode=SINGLE, height=15, width=30)
        self.Lb4.bind()

        cols = ['A', 'B']
        self.icon_tree = ttk.Treeview(self.gridroot, style="MyStyle.Treeview", columns=cols, padding=(5, 5),
                                      selectmode='browse', height=15, show='tree')
        ttk.Style().configure("MyStyle.Treeview", rowheight=36)
        self.icon_tree.column('A', anchor='center', minwidth=50)
        self.icon_tree.heading('A', text="bruh", anchor='center')
        self.icon_tree.column('B', anchor='center', minwidth=15)
        self.icon_tree.heading('B', text="bruh2", anchor='center')
        self.icon_tree.bind('<<TreeviewSelect>>', self.select_tree_item)

        cols2 = ['C', 'D']
        self.icon_tree2 = ttk.Treeview(self.gridroot, style="MyStyle.Treeview", columns=cols2, padding=(5, 5),
                                       selectmode='browse', height=15, show='tree')
        self.icon_tree2.column('C', anchor='center', minwidth=50)
        self.icon_tree2.heading('C', text="bruh", anchor='center')
        self.icon_tree2.column('D', anchor='center', minwidth=15)
        self.icon_tree2.heading('D', text="bruh2", anchor='center')
        self.icon_tree2.bind('<<TreeviewSelect>>', self.select_tree_item2)

    def monitor_sites_screen(self):
        widget_list = self.all_children(self.gridroot)
        for item in widget_list:
            item.grid_forget()

        self.icon_tree2.grid(column=0, row=2)
        self.Lb4.grid(column=1, row=2)
        self.Lb4.config(font=self.lb_font, selectmode=SINGLE, height=len(self.a_page_list))
        self.switch_apps_btn.grid(column=1, row=5)
        self.update_time_graphics_sites.grid(column=0, row=6)
        self.time_text.grid(column=0, row=7)
        self.add_monitor_site_btn.grid(column=0, row=3)
        self.rm_from_site_list_btn.grid(column=1, row=4)
        self.refresh_page_list_btn.grid(column=1, row=6)

        self.update_page_listbox()

    def monitor_apps_screen(self):
        widget_list = self.all_children(self.gridroot)
        for item in widget_list:
            item.grid_forget()

        self.Lb2.grid(column=2, row=2)
        self.Lb2.config(font=self.lb_font, selectmode=MULTIPLE, height=len(self.process_list))
        self.icon_tree.grid(column=0, row=2)
        self.rm_from_list_btn.grid(column=2, row=3)
        self.refresh_list_btn.grid(column=1, row=4)
        self.add_monitor_btn.grid(column=1, row=3)
        self.rm_from_list_btn.grid(column=2, row=4)
        self.switch_sites_btn.grid(column=2, row=6)
        self.update_time_graphics_apps.grid(column=1, row=7)
        self.time_text.grid(column=2, row=7)

        self.update_proc_listbox()

    # things to debug and test
    def print_processes(self):
        for x in self.process_list:
            print(x.name, x.pid)

