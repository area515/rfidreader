'''
@author: Sean O'Bryan, Ross Hendrickson  
'''  

from Tkinter import *
import Tkinter
import tkMessageBox
import os
import subprocess
import rfid
import gnupg
import pygame

root = Tk()
root.wm_title("RFID Reader")
root.columnconfigure(0, weight=1)

# make a solenoid
solenoid = rfid.Solenoid(12, 10)
# make an rfid reader
reader = rfid.Reader(solenoid)
reader.start()

def play_sound(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def Refresher():

    if labelrfidoutput.cget("text") != reader.lastkey:
        play_sound('readtag.wav')
    labelrfidoutput.config(text=reader.lastkey)
    labelrfidoutput.after(1000, Refresher) # every second...

def encrypt(message):
    gpg = gnupg.GPG(gnupghome='/home/pi/.gnupg')
    unencrypted_string = message
    encrypted_data = gpg.encrypt(unencrypted_string, 'globalw2865@gmail.com')
    encrypted_string = str(encrypted_data)
    return encrypted_string

def Clear():
    labelrfidoutput.config(text="")
    entryname.delete(0, Tkinter.END)
    entryemail.delete(0, Tkinter.END)
    reader.lastkey = ""


def Submit():

    play_sound('submit.wav')
    name = entryname.get()
    email = entryemail.get()
    key = reader.lastkey
    message = "%s|%s|%s\n" % (name,email,key)
    with open("Output.txt", "a") as text_file:
        text_file.write(encrypt(message))
    tkMessageBox.showinfo("Success", "Your info was submited.")
    


# Vector group
labelframepersonalinfo = LabelFrame(root, text="Personal Info")
labelframepersonalinfo.grid(row=3, sticky = W+E+N+S )
labelframepersonalinfo.columnconfigure(1, weight=1)
labelframepersonalinfo.rowconfigure(0, weight=1)
labelframepersonalinfo.rowconfigure(1, weight=1)
labelframepersonalinfo.rowconfigure(2, weight=1)
labelframepersonalinfo.rowconfigure(3, weight=1)

#    Set Power label/entry
labelname = Label(labelframepersonalinfo, text="Name")
labelname.grid(row=0, column=0,stick = W)
entryname = Entry(labelframepersonalinfo, bd =5)
entryname.grid(row=0, column=1, stick = W+E)
#    Set Power label/entry
labelemail = Label(labelframepersonalinfo, text="Email")
labelemail.grid(row=1, column=0,stick = W)
entryemail = Entry(labelframepersonalinfo, bd =5)
entryemail.grid(row=1, column=1, stick = W+E)
#    Current Power lable/entry
labelkey = Label(labelframepersonalinfo, text="Key")
labelkey.grid(row=2, column=0, sticky = W)
labelrfidoutput = Label(labelframepersonalinfo, text="Scan your key...") #, textvariable=reader.lastkey)
labelrfidoutput.grid(row=2, column=1,sticky = W+E+N+S)
#    Open LinuxCNC Vector
buttonclear = Button(labelframepersonalinfo, text="Reset", command=Clear)
buttonclear.grid(row=3, columnspan=2,sticky = W+E+N+S)
#    Open LinuxCNC Vector
buttonsubmitinfo = Button(labelframepersonalinfo, text="Submit", command=Submit)
buttonsubmitinfo.grid(row=4, columnspan=2,sticky = W+E+N+S)

labelrfidoutput.after(1000, Refresher) # every second...
#.showinfo(title, message, options)

root.mainloop()
