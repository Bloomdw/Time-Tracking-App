import psutil
import time
import ctypes
from ctypes import wintypes
import win32
import threading
import traceback
import json
from Misc import search_entry

user32 = ctypes.windll.user32

class Processes(object):
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
            with open("../assets/info.json", 'r') as f:
                info = json.load(f)
                json_info = info
                json_info = search_entry(info, "apps", self.name, self.time_active, "")

            with open("../assets/info.json", 'w') as f:
                json.dump(json_info, f, indent=1, sort_keys=True)

        except Exception as e:
            traceback.print_exc()

    def get_time(self):
        print("{:.2f}".format(self.time_active) + " name: " + self.name)

    @staticmethod
    def find_procname(name):
        for p in psutil.process_iter(attrs=['pid', 'name']):
            if name in p.info['name']:
                return p.pid

    @staticmethod
    def rem_windows_procs(pid, name):
        po = psutil.Process(pid)
        parent = po.parent()

        if name == "Registry" or name == "winlogon.exe" or name == "csrss.exe" or name == "wininit.exe" or name == "System" \
                or name == "System Idle Process" or name == "explorer.exe" or name == "Win32Bridge.Server.exe":
            return True

        while parent is not None:
            pname = parent.name()
            if pname == "winlogon.exe" or pname == "csrss.exe" or pname == "wininit.exe":
                return True

            ppid = parent.pid
            parent = psutil.Process(ppid).parent()

        return False

    #for debugging and testing purposes
    def create_file(self, name, pid, time_spent):
        f = open(str(name + "_programinfo"))
        f.write(str(name + "-" + pid + "-" + time_spent))