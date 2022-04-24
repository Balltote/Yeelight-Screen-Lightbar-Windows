from asyncio import events
from asyncio.subprocess import PIPE
from email.policy import default
from msilib.schema import Icon
import time
import os
import tempfile
import sys
import tkinter as tk
from tkinter import DISABLED, Button, ttk, Menu, colorchooser, messagebox
import pystray
from pystray import MenuItem as item
from yeelight import *
import yeelight as yl
from PIL import Image,ImageTk
import threading
from yeelight.flows import *
import subprocess


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# First we open the file containing a placeholder
try:
    tempfldr = tempfile.gettempdir()
    file = open(tempfldr+'/bulbIP.txt', 'r')
    text = file.read()
except FileNotFoundError:
  open(tempfldr+'/bulbIP.txt',"a")
pass
def get_bulbIP():
    # Creating a splashscreen before the program launches
    splash_window = tk.Tk()
    splash_window.title("Screen Lightbar Setup")
    w = 300
    h = 150
    splash_window.minsize(w, h)
    splash_window.maxsize(w, h)
    ws = splash_window.winfo_screenwidth()
    hs = splash_window.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    splash_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    splash_window.iconbitmap(resource_path(r"images/myicon.ico"))
    set_button_image=tk.PhotoImage(file=resource_path("images/set.png"))
    label = tk.Label(splash_window, text="Please Enter the Screen Lightbar IP ")
    label.pack(padx=5, pady=5, side="top")
    #splash_window.bind("<Return>", save_bulb)

    IP = tk.StringVar()
    entry = tk.Entry(splash_window, width=20, textvariable=IP)
    entry.pack(padx=5, pady=5, side="top")
    entry.focus_force()

    def keybinding(evnt):
        bulb = entry.get()
        with open(tempfldr+"/bulbIP.txt", "w") as reader:
            reader.truncate(0) # Here it's just to keep the IP part and no whitespaces-
            reader.write(bulb)
        splash_window.destroy()
        

    def save_bulb():
        bulb = entry.get()
        with open(tempfldr+"/bulbIP.txt", "w") as reader:
            reader.truncate(0) # Here it's just to keep the IP part and no whitespaces-
            reader.write(bulb)
        splash_window.destroy() # After the button is pressed and that a valid IP is input it closes the window

    # This button calls the function declared higher
    splash_window.bind("<Return>", save_bulb)
    set_btn = tk.Button(splash_window, image=set_button_image, borderwidth=0, command=save_bulb)
    set_btn.pack(padx=5, pady=5, side="bottom")
    splash_window.bind("<Return>", keybinding)
    splash_window.mainloop()

# Check if the IP is valid
def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

file = open(tempfldr+"/bulbIP.txt", "r")
text = file.read()
while not validate_ip(text):
  get_bulbIP()
  file.close()
  file = open(tempfldr+"/bulbIP.txt", "r")
  text = file.read()
  file.close()
#identify the Bulb
  bulb = yl.Bulb(text, effect="smooth", model="color")

#shutdown the light
def shutdown():
   file = open(tempfldr+'/bulbIP.txt', 'r')
   text = file.read()
   bulb = yl.Bulb(text, effect="smooth", model="color")
   try:  
        bulb.turn_off(light_type=LightType.Ambient)
        bulb.turn_off()
        #sys.exit()
   except BulbException as e:
        print(str(e))
        #sys.exit()

#Thread to shutdown the light and exit the program
def menu_quit():
    try:
        threading.Thread(target=shutdown).start()
        sys.exit()
    except BulbException as e:
        print(str(e))
        pass

# This is our main window
main_window = tk.Tk()
w = 500
h = 470
main_window.minsize(w, h)
main_window.maxsize(w, h)
ws = main_window.winfo_screenwidth()
hs = main_window.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
main_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
main_window.iconbitmap(resource_path(r"images/myicon.ico"))
main_window.title("Yeelight Screen LightBar Controller")
menubar = Menu(main_window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit Program", command=menu_quit)
menubar.add_cascade(label="File", menu=filemenu)
main_window.config(menu=menubar)


bulb = yl.Bulb(text, effect="smooth", model="color")
#test network connectivity
try:
    result = bulb.get_properties()
    print(result)
except BulbException as e:
    tk.messagebox.showerror(title="Network Error", message='Please Check Network Connectivity\n' + str(e))
    sys.exit()


color_picker_button_image = tk.PhotoImage(file=resource_path("images/color.png"))
switch_off_img = tk.PhotoImage(file=resource_path("images/switch-off-default.png"))
switch_on_img = tk.PhotoImage(file=resource_path("images/switch-on-default.png"))
yellow_light_button_image = tk.PhotoImage(file=resource_path("images/yellow.png"))
normal_light_button_image = tk.PhotoImage(file=resource_path("images/normal_button.png"))
white_light_button_image = tk.PhotoImage(file=resource_path("images/white_button.png"))
edit_button_image = tk.PhotoImage(file=resource_path("images/edit.png"))
switch_front_on_img = tk.PhotoImage(file=resource_path("images/on.png"))
switch_front_off_img = tk.PhotoImage(file=resource_path("images/off.png"))
ambilight_on_img = tk.PhotoImage(file=resource_path("images/amon.png"))
ambilight_off_img = tk.PhotoImage(file=resource_path("images/amoff.png"))

# open bulbIP.txt in default texteditor
def openInstruction():
    temp = os.environ['TEMP']
    textfile = os.path.join(temp, 'bulbIP.txt')
    subprocess.call(['notepad.exe',textfile])
    
# quit program after printing a message
def quit():
    tk.messagebox.showinfo(title="Restart", message="The program auto restart")
    os.execl(sys.executable, sys.executable, *sys.argv) #auto restart program code
    

# Combines n functions
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)

    return combined_func

def scale_to_ambilight(va2):
    bulb.set_brightness(int(va2), light_type=LightType.Ambient)
    print(bulb.get_properties()["bg_bright"])

    # This is the slider to set the Ambilight brightness, it only works every 10 ticks because of API limitation
brightness_scale = tk.Scale(main_window, orient="horizontal", from_=0, to=100, length=400, width=20, tickinterval=50,
                                resolution=1, label="Ambilight Light Brightness", command=scale_to_ambilight)
                                #resolution=10, bg="#2424ff", borderwidth=0, activebackground="#2424ff",
                                #sliderrelief="flat", troughcolor="#C4C4C4")
brightness_scale.place(x=50, y=150)
brightness_scale.set(bulb.get_properties()["bg_bright"]) # Check the state of slider

    
def scale_to_bulb(val):
    bulb.set_brightness(int(val), light_type=LightType.Main)
    print(bulb.get_properties()["bright"])

    # This is the slider to set the Main Light brightness, it only works every 10 ticks because of API limitation
brightness_scale = tk.Scale(main_window, orient="horizontal", from_=0, to=100, length=400, width=20, tickinterval=50,
                                resolution=1, label="Front Light Brightness", command=scale_to_bulb)
                                #resolution=10, bg="black", borderwidth=0, activebackground="#2424ff",
                                #sliderrelief="flat", troughcolor="#C4C4C4")
brightness_scale.place(x=50, y=350)
brightness_scale.set(bulb.get_properties()["bright"]) # Check the state of slider

OPTIONS = [
        "Default",
        "Alarm",
        "Candle flicker",
        "Christmas",
        "Date night",
        "Disco",
        "Happy birthday",
        "LSD",
        "Movie",
        "Night mode",
        "Police",
        "Police 2",
        "Random loop",
        "RGB",
        "Romance",
        "Slowdown",
        "Strobe",
        "Strobe color",
        "Sunrise",
        "Sunset",
        "Temp"
    ]
variable = tk.StringVar(main_window)
variable.set(OPTIONS[0])

    # Toggle between options in the combobox
def ok(event):
    if combobox_dropdown.get() == "Alarm":
        bulb.start_flow(yl.flows.alarm(duration=250), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Candle flicker":
        bulb.start_flow(yl.flows.candle_flicker(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Christmas":
        bulb.start_flow(yl.flows.christmas(duration=250, brightness=100, sleep=3000), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Date night":
        bulb.start_flow(yl.flows.date_night(duration=500, brightness=50), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Disco":
        bulb.start_flow(yl.flows.disco(bpm=120), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Happy birthday":
        bulb.start_flow(yl.flows.happy_birthday(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "LSD":
        bulb.start_flow(yl.flows.lsd(duration=3000, brightness=100), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Movie":
        bulb.start_flow(yl.flows.movie(duration=500, brightness=50), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Night mode":
        bulb.start_flow(yl.flows.night_mode(duration=500, brightness=1), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Police":
        bulb.start_flow(yl.flows.police(duration=300, brightness=100), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Police2":
        bulb.start_flow(yl.flows.police2(duration=250, brightness=100), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Random loop":
        bulb.start_flow(yl.flows.random_loop(duration=750, brightness=100, count=9), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "RGB":
        bulb.start_flow(yl.flows.rgb(duration=250, brightness=100, sleep=3000), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Romance":
        bulb.start_flow(yl.flows.romance(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Slowdown":
        bulb.start_flow(yl.flows.slowdown(duration=2000, brightness=100, count=8), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Strobe":
        bulb.start_flow(yl.flows.strobe(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Strobe color":
        bulb.start_flow(yl.flows.strobe_color(brightness=100), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Sunrise":
        bulb.start_flow(yl.flows.sunrise(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Sunset":
        bulb.start_flow(yl.flows.sunset(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Temp":
        bulb.start_flow(yl.flows.temp(), light_type=LightType.Ambient)
    elif combobox_dropdown.get() == "Default":
        bulb.stop_flow(light_type=LightType.Ambient)

            # Hack to avoid blue selection on dropdown menu
def defocus(event):
    event.widget.master.focus_set()

combobox_dropdown = ttk.Combobox(main_window, state="readonly", value=OPTIONS, justify="center", width=15)
combobox_dropdown.current(0)

        # To get live selection, it avoid the usage of a button
combobox_dropdown.bind("<<ComboboxSelected>>", ok)
combobox_dropdown.bind("<FocusIn>", defocus)
combobox_dropdown.place(x=100, y=15)

        # Color
combobox_dropdown.option_add("*TCombobox*Listbox.selectBackground", "#0000FF")
combobox_dropdown.option_add("*TCombobox*Listbox.selectForeground", "white")

def color():
    color = colorchooser.askcolor()[0]
    bulb.set_rgb(color[0], color[1], color[2], light_type=LightType.Ambient)

    # Color picker is bundled in the tkinter module
color_picker_button = tk.Button(main_window, image=color_picker_button_image, borderwidth=0, command=color)

color_picker_button.place(x=50, y=75)

    # Bellow we have 3 buttons for white light these are workarounds to reset white light after color light
yellow_light_button = tk.Button(main_window, image=yellow_light_button_image,
                                    command=lambda: bulb.set_color_temp(2800), height=95, borderwidth=0)
yellow_light_button.place(x=50, y=260)

normal_light_button = tk.Button(main_window, image=normal_light_button_image,
                                    command=lambda: bulb.set_color_temp(4600), height=95, borderwidth=0)
normal_light_button.place(x=160, y=260)

blue_light_button = tk.Button(main_window, image=white_light_button_image,
                                  command=lambda: bulb.set_color_temp(6500), height=95, borderwidth=0)
blue_light_button.place(x=260, y=260)

edit_button = tk.Button(main_window, image=edit_button_image, 
                command=combine_funcs(openInstruction, quit), height=30, borderwidth=0)
edit_button.place(x=10, y=10)

 # system tray icon
    # Define a function for quit the window
def quit_window(icon, item):
    bulb.stop_flow(light_type=LightType.Ambient)
    threading.Thread(target=shutdown).start()
    icon.stop()
    icon.notify("Program Closed", title="Notification")
    main_window.destroy()
    sys.exit()

    # Define a function to show the window again
def show_window(icon, item):
    icon.stop()
    main_window.after(0,main_window.deiconify())
    
def hide_window():
    trayicon = Image.open(resource_path("images/myicon.ico"))
    menu = pystray.Menu(item('Show', show_window, default=True, visible=True), item('Quit', quit_window))
    icon = pystray.Icon("name", trayicon, "Yeelight LightBar Controller", menu)
    main_window.withdraw()
    icon.run()
  
main_window.protocol('WM_DELETE_WINDOW', hide_window)

def init_btn_pressed():
    try:
        if bulb.get_properties()["bg_power"] == "on":
            ambi_button["state"] = "normal"
            return switch_on_img
        else:
            ambi_button["state"] = "disable"
            return switch_off_img
    except BulbException as e:
        print(str(e))
        tk.messagebox.showerror(title="Network Error", message=str(e))

def init_front_btn_pressed():
    try:
        if bulb.get_properties()["power"] == "on":
            return switch_front_on_img
        else:
            return switch_front_off_img 
    except BulbException as e:
        print(str(e))
        tk.messagebox.showerror(title="Network Error", message=str(e))

def switch_btn_pressed():
    bulb.stop_flow(light_type=LightType.Ambient)
    bulb.toggle(light_type=LightType.Ambient)
    time.sleep(1)
    try:
        if bulb.get_properties()["power"] == "off":
            ambi_button["state"] = "disabled"
            button.config(image=switch_off_img, borderwidth=0)
            button1.config(image=switch_front_off_img, borderwidth=0)
            return(init_front_btn_pressed)
        elif bulb.get_properties()["bg_power"] == "off":
            ambi_button["state"] = "disabled"
            button.config(image=switch_off_img, borderwidth=0)
            return(init_btn_pressed)
        else:
             ambi_button["state"] ="normal"
             button.config(image=switch_on_img, borderwidth=0)
             button1.config(image=switch_front_on_img, borderwidth=0)
             return(init_btn_pressed)
    except BulbException as e:
        print(str(e))
        return(init_btn_pressed)

def switch_front_btn_pressed():
    try:
        bulb.stop_flow(light_type=LightType.Ambient)
        bulb.dev_toggle()
        time.sleep(1)
        if bulb.get_properties()["power"] == "on":
            button1.config(image=switch_front_on_img, borderwidth=0)
            ambi_button.config(state='normal')
            button.config(image=switch_on_img, borderwidth=0)
            return(init_front_btn_pressed)
        else:
            button1.config(image=switch_front_off_img, borderwidth=0)
            ambi_button.config(state='disabled')
            button.config(image=switch_off_img, borderwidth=0)
            return(init_front_btn_pressed)
    except Exception as e:
        print(str(e))
        button.config(image=switch_off_img, borderwidth=0)
        button1.config(image=switch_front_off_img, borderwidth=0)
        return(init_front_btn_pressed)

def launchWithoutConsole(command, args):
   """Launches 'command' windowless"""
   startupinfo = subprocess.STARTUPINFO()
   startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

   return subprocess.Popen([command] + args, startupinfo=startupinfo,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)

t1 = None
def ambi_on():
    global t1
    flowfile = resource_path("include/ambilight.py")
    if  combobox_dropdown['justify'] == "center":
            #print('process PID', t1.pid)
         ambi_button.config(image=ambilight_on_img)
         combobox_dropdown.config(state="disabled", justify="left")
         t1 = launchWithoutConsole('python', [flowfile])
         print(t1.returncode)
         print(t1.pid)
    else:
         ambi_button.config(image=ambilight_off_img)
         combobox_dropdown.config(state="readonly", justify="center")
         t1.kill()
         print(t1.communicate())
         print(t1.returncode)
         bulb.stop_flow(light_type=LightType.Ambient)

ambi_button = tk.Button(main_window, image=ambilight_off_img, state="disabled", command=ambi_on, height=95, borderwidth=0)
ambi_button.place(x=180, y=60)
      # Toggle button calls a function to check whether the light is on or off. Thanks to this we have a
    # dynamic button
button = tk.Button(main_window, image=init_btn_pressed(), command=switch_btn_pressed, height=95, borderwidth=0)
button.place(x=350, y=60)

    #Toggle button for Front main light
button1 = tk.Button(main_window, image=init_front_btn_pressed(), command=switch_front_btn_pressed, height=95, borderwidth=0)
button1.place(x=360, y=260)

main_window.mainloop()
