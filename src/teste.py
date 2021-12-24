import subprocess
from PIL import Image, ImageTk, ImageChops

subprocess.run(["icoextract", "C:\Program Files\JetBrains\PyCharm Community Edition 2021.2.3\\bin\pycharm64.exe", "../lol.png"], shell=True)
img = Image.open("../lol.png")
resized_img = img.resize((36, 36))
resized_img.save("../lol.png")