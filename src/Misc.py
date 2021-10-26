import ctypes
from ctypes import wintypes
import win32
import win32ui
import win32gui
import win32con
import win32api
import json
import re
import traceback
from PIL import Image, ImageTk, ImageChops
import favicon
import requests
from io import BytesIO

#Returns number values to be displayed on the GUI
def search_vals(name, Type):
    nums = []

    try:
        with open("../assets/info.json", 'r') as d:
            j_obj = json.load(d)

            if Type not in j_obj:
                j_obj[Type] = []

            for idx, obj in enumerate(j_obj[Type]):
                cur = obj['name']

                if cur == name:
                    nums = [obj['seconds'], obj['minutes'], obj['hours'], obj['week'],
                            obj['name']]

    except Exception as e:
        print(e)
        traceback.print_exc()

    return nums

#Updates all json info
def search_entry(info, Type, name, secs, url):
    j_obj = info

    if Type not in j_obj:
        print("no type (shouldn't get here tbh")
        j_obj[Type] = []

    for idx, obj in enumerate(j_obj[Type]):
        cur = obj['name']

        if cur == name:
            c_secs = obj['seconds'] + secs

            j_obj[Type][idx] = {
                'name': name,
                'seconds': c_secs,
                'minutes': c_secs // 60,
                'hours': (c_secs // 60) // 60,
                'week': ((c_secs // 60) // 60) / 7,
                'url': url
            }

            return j_obj

    j_obj[Type].append({
        'name': name,
        'seconds': 0,
        'minutes': 0,
        'hours': 0,
        'week': 0,
        'url': ""
    })

    return j_obj

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

    img.save('../assets/icon.png')

    # hbmp.SaveBitmapFile(hdc, 'icon.bmp')

    img = Image.open("../assets/icon.png")

    return img

def page_icon(data):
    defic = Image.open("../assets/deficon.png")
    url = data
    if data == '' or not data or data is None:
        return defic

    try:
        thing = url.partition("chrome://favicon/")[2]
        icon = favicon.get(thing)
        ic = requests.get(icon[0].url)
        im = Image.open(BytesIO(ic.content))
        im = im.resize((36, 36))
        return im
    except Exception as e:
        #print(e)
        #traceback.print_exc()
        return defic

def url_strip(url):
    if "http://" in url or "https://" in url:
        url = url.replace("https://", '').replace("http://", '')\
            .replace('\"', '')
    if "/" in url:
        url = url.split('/', 1)[0]

    return url

def search_thing(r):
    rpl = str(r[0])
    day = re.search(r"^.*\:([^-]*),.*$", rpl)
    return day

def get_list(Type):
    list = []

    try:
        with open("../assets/info.json", 'r') as d:
            j_obj = json.load(d)

            if Type not in j_obj:
                j_obj[Type] = []

            for idx, obj in enumerate(j_obj[Type]):
                list.append((obj['name'], obj['url']))
    except Exception as e:
        print(e)
        traceback.print_exc()

    return list
