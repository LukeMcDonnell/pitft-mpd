#!/usr/bin/python
from time import *
from subprocess import *
import Adafruit_CharLCD as LCD
import urllib
import thread
from threading import Thread
import StringIO 
import pygame
from pygame.locals import *
import os 
import gc
import signal
import sys
from lfmutils import LastfmFrontend
from mpdutils import MPDClientFrontend

### PYGAME init 
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

pygame.init()
pygame.mouse.set_visible(0)
size = width, height = 480, 320
screen = pygame.display.set_mode(size)

import LCDui

###LASTFM CONNECT
lastfm = LastfmFrontend()
lastfm.connect()

### MPD CONNECT
mpdutil = MPDClientFrontend()

### LCD CONNECT
try:
	lcd = LCD.Adafruit_CharLCDPlate()
	lcd.clear()
	lcd.message("    MusicBox\n")
	lcd.message("  Initializing")
except:
	print ("LCD Failed to init")
	lcd = None

uiLCD = LCDui.uiLCD(lastfm,mpdutil,screen,lcd)

# START THREADS
thread.start_new_thread(uiLCD.mpd_thread, ())
thread.start_new_thread(uiLCD.loop_thread, ())
for i in range(3):
	q=Thread(target=uiLCD.queue_thread)
	q.daemon=True
	q.start()

# WAIT FOR EXIT
def signal_handler(signal, frame):
        print('Exiting...')
	#uiLCD.update_LCD("   Exiting..."," ")
	uiLCD.LCD.clear()
	uiLCD.lcd.message("   Exiting..."[:16]+'\n'+" "[:16])
	mpdutil.client.close()
	mpdutil.client.disconnect()
	print('Closed MPD')
	pygame.quit()
	print('Quit pygame')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.pause()

while 1:
	sleep(100000000)
