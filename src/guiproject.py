from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageChops
import psutil
import time
import ctypes
from ctypes import wintypes
import win32
import win32ui
import win32gui
import win32con
import win32api
import threading
from flask import Flask, jsonify, request
import json
import datetime
import os
from pathlib import Path
import traceback

gridroot= tk.Tk()
gridroot.geometry("1600x1600")

height = 800
width = 900

process_list = []
a_process_list = []
a_page_list = []
cur_selections = []
mon_procs = []
dup_proc_names = set()
icons = []
lb_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
user32 = ctypes.windll.user32
tab_list = []

def search_entry(info, Type, name, secs):
    j_obj = info
    print(j_obj)

    if Type not in j_obj:
        print("no type (shouldn't get here tbh")
        j_obj[Type] = []

    for idx, site in enumerate(j_obj[Type]):
        cur = site['name']

        if cur == name:
            c_secs = site['seconds'] + secs

            j_obj[Type][idx] = {
                'name': name,
                'seconds': c_secs,
                'minutes': c_secs // 60,
                'hours': (c_secs//60) // 60,
                'week': ((c_secs//60) // 60) / 7
            }

            return j_obj

    j_obj[Type].append({
            'name': name,
            'seconds': secs,
            'minutes':0,
            'hours': 0,
            'week': 0
        })

    return j_obj

class processes(object):
    def __init__(self, name, pid, exe):
        self.name = name
        self.pid = pid
        self.exe = exe
        self.time_spent = 0
        self.time_active = 0
        p1 = threading.Thread(target=self.check_loop, args=())
        p1.start()

    def check_window(self):
        h_wnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
        p = psutil.Process(pid.value)

        name = str(p.name())
        name2 = str(self.name)

        if name == name2:
            return True

        return False

    def check_loop(self):
        t = 0
        start_time = time.time()

        #While the process is running, check if foreground window (window currently being used) is the same as the process
        while self.check_window() == True:
            t = time.time() - start_time

        #Log the total time the user spent using the window
        self.time_active += t
        self.time_spent = time.perf_counter()
        time.sleep(1)

        json_info = {}

        try:
            with open("info.json", 'r') as f:
                info = json.load(f)
                json_info = info
                json_info = search_entry(info, 'apps', self.name, self.time_active)

        except Exception as e:
            traceback.print_exc()
            return

        with open("info.json", 'w') as f:
            json.dump(json_info, f, indent=2, sort_keys=True)

    def get_time(self):
        print("{:.2f}".format(self.time_active) + " name: " + self.name)

    def create_file(self, name, pid, time_spent):
        f = open(str(name + "_programinfo"))
        f.write(str(name + "-" + pid + "-" + time_spent))

def find_procname(name):
    for p in psutil.process_iter(attrs=['pid','name']):
        if name in p.info['name']:
            return p.pid

def print_processes():
    for x in process_list:
        print(x.name, x.pid)

def add_to_monitor_list():
    for c in Lb.curselection():
        name = Lb.get(c)
        pid = find_procname(name)
        mon_procs.append(name)
        create_proc_listbox2(name, pid)

def create_process(info, pid, exe):
    return processes(info, pid, exe)

def del_selections():
    for s in Lb.curselection():
        Lb.delete(s)

def del_selections_2():
    for s in Lb2.curselection():
        Lb2.delete(s)

def rem_monitor_sels():
    for s in Lb2.curselection():
        name = Lb.get(s)
        for idx, i in enumerate(process_list):
            if name == i.name:
                process_list.remove(idx)

def display_time():
    for s in Lb.curselection():
        for e in process_list:
            if Lb.get(s) == e.name:
                e.get_time()

def search_vals(name, Type):
    nums = []

    try:
        with open("info.json", 'r') as d:
            j_obj = json.load(d)

            for idx, site in enumerate(j_obj[Type]):
                cur = site['name']

                if cur == name:
                    nums = [site['seconds'], site['minutes'], site['hours'], site['week'],
                            site['name']]

    except Exception as e:
        print(e)
        traceback.print_exc()

    return nums

def create_canvas():
    background_image = ImageTk.PhotoImage(Image.open('landscape.jpg'))
    background_label = tk.Label(gridroot, image=background_image)
    background_label.photo = background_image
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

def welcome_screen():
    watchlist_btn.grid(column=0, row=0)
    main_title.grid(column=0, row=1)

def all_children(window):
    _list = window.winfo_children()

    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())

    return _list

def monitor_sites_screen():
    widget_list = all_children(gridroot)
    for item in widget_list:
        item.grid_forget()

    Lb3.grid(column=1, row=2)
    Lb3.config(font=lb_font, selectmode=MULTIPLE, height=len(a_page_list))
    Lb4.grid(column=2, row=2)
    Lb4.config(font=lb_font, selectmode=SINGLE, height=len(a_page_list))
    switch_apps_btn.grid(column=2, row=5)

    p3 = threading.Thread(target=create_page_listbox(), args=())
    p3.start()

def monitor_apps_screen():
    widget_list = all_children(gridroot)
    for item in widget_list:
        item.grid_forget()

    Lb.grid(column=1, row=2)
    Lb.config(font=lb_font, selectmode=MULTIPLE, height=len(process_list))
    Lb2.grid(column=2, row=2)
    Lb2.config(font=lb_font, selectmode=MULTIPLE, height=len(process_list))
    icon_tree.grid(column=0, row=2)
    get_time_btn.grid(column=1, row=3)
    rm_from_list_btn.grid(column=2, row=3)
    refresh_list_btn.grid(column=1, row=4)
    add_monitor_btn.grid(column=2, row=4)
    switch_sites_btn.grid(column=2, row=5)

    p2 = threading.Thread(target=create_proc_listbox(), args=())
    p2.start()

def add_process(idx, name, pid, exe, didx):
    i = get_icon(exe)

    if i is None:
        return

    im = ImageTk.PhotoImage(i)
    icons.append(im)
    icon_tree.insert(parent='', index='end', image=icons[didx])

    Lb.insert(idx, name)
    a_process_list.append(name)
    process = create_process(name, pid, exe)
    process_list.append(process)

    return 1

def create_proc_listbox():
    didx = 0
    for idx, proc in enumerate(psutil.process_iter(attrs=['pid', 'name', 'exe'])):
        pid = proc.pid
        name = proc.name()
        po = psutil.Process(pid)
        parent = po.parent()

        if name in a_process_list:
            continue

        #adds process only if the name is not duplicated and that it's not a windows process
        if not rem_windows_procs(pid, name):
            exe = proc.exe()
            if parent is None:
                if add_process(idx, name, pid, exe, didx) is not None:
                    didx += 1
            elif parent.name() == "explorer.exe":
                if add_process(idx, name, pid, exe, didx) is not None:
                    didx += 1

def rem_windows_procs(pid, name ):
    po = psutil.Process(pid)
    parent = po.parent()

    if name == "Registry"or name == "winlogon.exe" or name == "csrss.exe" or name == "wininit.exe" or name == "System" \
            or name == "System Idle Process" or name == "explorer.exe" or name == "Win32Bridge.Server.exe":
        return True

    while parent is not None:
        pname = parent.name()
        if pname == "winlogon.exe" or pname == "csrss.exe" or pname == "wininit.exe":
            return True

        ppid = parent.pid
        parent = psutil.Process(ppid).parent()

    return False

def create_proc_listbox2(name, idx):
    Lb2.insert(idx, name)

def check_status(id):
    lol = psutil.win_service_get(id)
    if lol.STATUS_RUNNING:
        pass

def get_icon(exe):
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

    large, small = win32gui.ExtractIconEx(exe, 0)
    win32gui.DestroyIcon(small[0])

    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    hdc = hdc.CreateCompatibleDC()

    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), large[0])

    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGBA',
        (32, 32),
        bmpstr, 'raw', 'BGRA', 0, 1
    )

    extrema = img.convert("L").getextrema()
    if extrema[0] > 0:
        return

    img.resize((16, 16))
    img.save('icon.png')

    #hbmp.SaveBitmapFile(hdc, 'icon.bmp')

    img = Image.open("icon.png")

    return img

create_canvas()

main_title = tk.Message(text="The monitor 9000", bg="green", fg="blue")

watchlist_btn = tk.Button(gridroot, text='Program watchlist', bg='yellow', fg='red',
                   command=lambda: [monitor_apps_screen()])

add_monitor_btn = tk.Button(gridroot, text='Add to monitor list', bg='yellow', fg='red',
                   command=lambda: [add_to_monitor_list(), del_selections()])

get_time_btn = tk.Button(gridroot, text='How much time have I spent?', bg='yellow', fg='blue',
                    command=lambda: [display_time()])

rm_from_list_btn = tk.Button(gridroot, text='Remove from monitor list', bg='yellow', fg='red',
                    command=lambda: [rem_monitor_sels(), del_selections_2()])

refresh_list_btn = tk.Button(gridroot, text='Refresh program list', bg='yellow', fg='red',
                    command=lambda: [threading.Thread(target=create_proc_listbox())])

refresh__page_list_btn = tk.Button(gridroot, text='Refresh webpage list', bg='yellow', fg='red',
                    command=lambda: [create_page_listbox()])

switch_apps_btn = tk.Button(gridroot, text='Switch to apps page', bg='yellow', fg='red',
                    command=lambda: [monitor_apps_screen()])

switch_sites_btn = tk.Button(gridroot, text='Switch to sites page', bg='yellow', fg='red',
                    command=lambda: [monitor_sites_screen()])

def create_page_listbox():
    for idx, page in enumerate(tab_list):
        if page in a_page_list:
            continue

        Lb3.insert(idx, page)
        a_page_list.append(page)

Lb = tk.Listbox(gridroot, selectmode=MULTIPLE)
Lb2 = tk.Listbox(gridroot, selectmode=SINGLE)
Lb2.bind('<<ListboxSelect>>', lambda event: update_time_info(event, 'apps'))
Lb3 = tk.Listbox(gridroot, selectmode=MULTIPLE)
Lb4 = tk.Listbox(gridroot, selectmode=SINGLE)
Lb4.bind('<<ListboxSelect>>', lambda event: update_time_info(event, 'sites'))

cols = ['A']
icon_tree = ttk.Treeview(gridroot, columns=cols, selectmode='none', height=14, show='tree', style="MyStyle.Treeview")
ttk.Style().configure("MyStyle.Treeview", rowheight=36)
icon_tree.column('A', anchor=CENTER, width=20)
icon_tree.heading('A', text="bruh2", anchor=CENTER)
time_text = Text(gridroot, font=lb_font, height=20)

welcome_screen()

app = Flask(__name__)
app.app_context().push()
url_timestamp = {}
url_viewtime = {}
prev_url = ""

def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

fthread = threading.Thread(target=start_flask).start()

def url_strip(url):
    url = re.sub("/^(?:http:\/\/(.+)){2}/", "", url)
    return url

def search_thing(r):
    rpl = str(r[0])
    day = re.search(r"^.*\:([^-]*),.*$", rpl)
    return day

@app.route('/send_url', methods=['POST'])
def send_url():
    url = request.form["url"]
    ic = request.form["ic_link"]
    url = url_strip(url)
    print("url=" + url)

    parent_url = url

    global url_timestamp
    global url_viewtime
    global prev_url

    if parent_url not in url_timestamp.keys():
        url_viewtime[parent_url] = 0

    time_spent = 0

    if prev_url != '':
        time_spent = int(time.time() - url_timestamp[prev_url])
        url_viewtime[prev_url] = url_viewtime[prev_url] + time_spent

    x = int(time.time())
    url_timestamp[parent_url] = x
    prev_url = parent_url

    tday = datetime.datetime.today()
    ttp = tday.timetuple()
    day = ttp[2]

    json_info = {}
    js_list = []

    try:
        with open("info.json", 'r') as f:
            info = json.load(f)
            json_info = info
            json_info = search_entry(info, 'sites', url, time_spent)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': 'nope nope!'}), 200

    with open("info.json", 'w') as f:
        print(json_info)
        json.dump(json_info, f, indent=2)

    return jsonify({'message': 'success!'}), 200

@app.route('/quit_url', methods=['POST'])
def quit_url():
    resp_json = request.get_data()
    print("Url closed: " + resp_json.decode())
    return jsonify({'message': 'quit success!'}), 200

if __name__ == "__main__":
    gridroot.update()
    gridroot.mainloop()













