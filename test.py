import subprocess

from Utils import Utils
import os
import customtkinter
import tkinter
import tkinter.messagebox
import shlex
import sys
import time
from threading import Thread

root = "/home/haylo/Documents/University/SCAV/Video/P3/"
os.chdir(root)

shm_root = "/dev/shm/dash/"

key_id, key = Utils.generate_keys('encryption_key_id.key', 'encryption_key.key', shm_root)

print(key_id, key)



