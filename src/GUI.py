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
from Misc import get_icon, search_entry, search_vals, get_list, page_icon

class GUI_class:
    def __init__(self, width, height):
        self.gridroot = tk.Tk()
        self.height = height
        self.width = width
        self.lb_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
        self.process_list = []
        self.a_process_list = []
        self.a_page_list = []
        self.tab_list = []
        self.mon_procs = []
        self.mon_sites = []
        self.dup_proc_names = set()
        self.icons = []
        self.user32 = ctypes.windll.user32
        self.create_buttons()
        self.create_listboxes()
        self.welcome_screen()

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
            print("lol1")
            return

        for s in cur:
            self.Lb2.delete(s)

    def del_selections_sites(self):
        self.icon_tree2.delete(self.icon_tree.focus())

    def del_selections_sites2(self):
        cur = self.Lb4.curselection()
        if not cur:
            print("lol3")
            return

        for s in cur:
            self.Lb4.delete(s)

    def rem_monitor_sels(self):
        cur = self.Lb2.curselection()
        if not cur:
            print("lol4")
            return

        for s in cur:
            name = self.Lb2.get(s)
            for i in enumerate(self.process_list[:]):
                if name == i.name:
                    self.process_list.remove(i)

    def rem_monitor_sels_sites(self):
        cur = self.Lb4.curselection()
        if not cur:
            print("lo5")
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
        self.time_text = Text(self.gridroot, font=self.lb_font, height=1, padx=5, pady=5, width=7)
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
        self.time_text.delete('1.0', END)
        cur = self.Lb2.curselection()
        name = self.Lb2.get(cur)
        vals = search_vals(name, "apps")
        self.time_text.insert(INSERT, vals[0])
        self.time_text.insert(INSERT, vals[1])
        self.time_text.insert(INSERT, vals[2])
        self.time_text.insert(INSERT, vals[3])

    def display_site_time(self):
        self.time_text.delete('1.0', END)
        cur = self.Lb4.curselection()
        name = self.Lb4.get(cur)
        vals = search_vals(name, "sites")
        self.time_text.insert(INSERT, vals[0])
        self.time_text.insert(INSERT, vals[1])
        self.time_text.insert(INSERT, vals[2])
        self.time_text.insert(INSERT, vals[3])
        return name

    def add_process(self, idx, name, pid, exe, didx):
        i = get_icon(exe)

        if i is None:
            return

        im = ImageTk.PhotoImage(i)
        self.icons.append(im)
        self.icon_tree.insert(parent='', index='end', image=im, values=(str(name)))

        self.a_process_list.append(name)
        process = self.create_process(name, pid, exe)
        self.process_list.append(process)
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

            if name in self.a_process_list:
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
            if str(page[0]) in self.a_page_list:
                continue

            name = str(page[0])
            imdata = str(page[1])

            img = ImageTk.PhotoImage(page_icon(imdata))

            self.icon_tree2.insert(parent='', index='end', image=img, values=(str(name)))
            self.a_page_list.append(name)

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

        self.refresh__page_list_btn = tk.Button(self.gridroot, text='Refresh webpage list', bg='#3E3432', fg='#FB6F14',
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

        cols2 = ['A', 'B']
        self.icon_tree2 = ttk.Treeview(self.gridroot, style="MyStyle2.Treeview", columns=cols2, padding=(5, 5),
                                       selectmode='browse', height=15, show='tree')
        ttk.Style().configure("MyStyle2.Treeview", rowheight=36)
        self.icon_tree2.column('A', anchor='center', minwidth=50)
        self.icon_tree2.heading('A', text="bruh", anchor='center')
        self.icon_tree2.column('B', anchor='center', minwidth=15)
        self.icon_tree2.heading('B', text="bruh2", anchor='center')
        self.icon_tree2.bind('<<TreeviewSelect>>', self.select_tree_item2)

    def monitor_sites_screen(self):
        widget_list = self.all_children(self.gridroot)
        for item in widget_list:
            item.grid_forget()

        self.icon_tree2.grid(column=0, row=2)
        self.Lb4.grid(column=2, row=2)
        self.Lb4.config(font=self.lb_font, selectmode=SINGLE, height=len(self.a_page_list))
        self.switch_apps_btn.grid(column=2, row=5)
        self.update_time_graphics_sites.grid(column=1, row=6)
        self.time_text.grid(column=1, row=7)
        self.add_monitor_site_btn.grid(column=1, row=3)
        self.rm_from_site_list_btn.grid(column=2, row=4)

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

