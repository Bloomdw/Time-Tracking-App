from GUI import GUI_class
from Flask_serv import run_flask

if __name__ == "__main__":
    run_flask()
    gui = GUI_class("1300",  "1000")
    gui.mainloop()
