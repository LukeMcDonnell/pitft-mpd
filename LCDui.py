#!/usr/bin/python
from time import *
from subprocess import *
import Adafruit_CharLCD as LCD
import urllib
import thread
import Queue
import StringIO 
import pygame
from pygame.locals import *
import os 
import gc
import signal
import sys
from lfmutils import LastfmFrontend
from mpdutils import MPDClientFrontend


class uiLCD:
	def __init__(self,lastfm,mpdutil,screen,lcd):
		self.lcd 	= lcd
		self.lastfm 	= lastfm
		self.mpdutil	= mpdutil
		self.screen	= screen
		# Paths
		self.path = "/usr/local/bin/LCD/"# os.path.dirname(sys.argv[0]) + "/"
		#os.chdir(self.path)
				
		#Font & Txt
		fontfile = self.path + 'helvetica-neue-bold.ttf'
		#print fontfile
		self.font = {}
		self.font['details'] = pygame.font.Font(fontfile, 13)
		self.font['field'] = pygame.font.Font(fontfile, 23)

		## Define
		self.defaultImg = self.path + 'default.jpg'
		a = StringIO.StringIO(urllib.urlopen(self.defaultImg).read())
		b = pygame.image.load(a)
		self.defaultImg_io = pygame.transform.scale(b,(280,280))

		self.line1 = ''
		self.line2 = ''

		# Now playing 
		self.state = 		'NA'
		self.album = 		'NA'
		self.title = 		'NA'
		self.artist= 		'NA'
		self.plpos = 		0
		self.pllen =		0
		self.playlist= 	''
		
		self.cover_cache = []
		self.cover_queue = Queue.PriorityQueue()
		
		# Updates
		self.updatetrack=True
		self.updatealbum=True
		self.updatecoverqueue=False
		self.coverwait=False

	def update_LCD(self):
		if self.state == 'play':
			l1 = self.artist
			l2 = self.title
		elif self.state == 'pause':
			l1 = "    MusicBox"
			l2 = "     Paused"
		elif self.state == 'disconnected':
			l1 = "    MusicBox"
			l2 = "   Connecting"
		else:
			l1 = "    MusicBox"
			l2 = "     Ready"
			
		if l1 != self.line1 or l2 != self.line2:
			self.lcd.clear()
			self.lcd.message(l1[:16]+'\n'+l2[:16])
			print ('LCD1: ' + l1[:16])
			print ('LCD2: ' + l2[:16])
		self.line1 = l1
		self.line2 = l2


	def update_text(self):
		#Wipe the text areas.
		self.screen.fill(0, (280,0,200,280))
		self.screen.fill((255,255,255),(0,280,480,40))
	
		#NOW PLAYING
		if (self.state == "play" or self.state == "pause"):
			l1 = self.title
			l2 = self.artist + ' (' + self.album + ')'
		elif self.state == 'disconnected':
			l1 = "Connecting..."
			l2 = "Please Wait"
		else:
			l1 = "MusicBox Ready"
			l2 = "192.168.1.90"
		
		text = self.font["field"].render(l1, 1,(0,0,0))
		self.screen.blit(text, (10, 278)) # Track
		text = self.font["details"].render(l2, 1,(0,0,0))
		self.screen.blit(text, (10, 302)) # Artist
		
		#PLAYLIST
		text = self.font["details"].render('PLAYLIST', 1,(230,228,227))
		self.screen.blit(text, (285, 3)) #next
		
		if (self.playlist):
			i=1
			while i <= 13 and i+self.plpos < self.pllen:
				words =  self.playlist[i+self.plpos]['title']
				text = self.font["details"].render(words, 1,(230,228,227))
				self.screen.blit(text, (285, 3 + (i*19))) 
				i = i + 1
		pygame.display.update()


	def display_img(self,img):
			self.screen.blit(img,(0,0))
			pygame.display.update()
		
	def update_cover(self):
		## SEARCH CACHE
		for i in range(len(self.cover_cache)):
			if self.cover_cache[i][0] == self.artist:
				for n in range(len(self.cover_cache[i][1])):
					if self.cover_cache[i][1][n][0] == self.album:
						#print "Displaying image: " + self.cover_cache[i][1][n][1]
						self.display_img(self.cover_cache[i][1][n][2])
						self.coverwait=False
						return(0)
						break
						
		## NOT IN CACHE.
		#print "Not in cache. Using Default while we wait"	
		self.display_img(self.defaultImg_io)
		self.coverwait = True
		return(1)
		
	def get_cover(self,item):
		artist = item[0]
		album = item[1]
		title = item[2]
		artistID = -1
		## CHECK CACHE BEFORE WE SEARCH
		for i in range(len(self.cover_cache)):
			if self.cover_cache[i][0] == artist:
				artistID = i		
				for n in range(len(self.cover_cache[i][1])):
					if self.cover_cache[i][1][n][0] == album:
						return(0)
				
		album_uri = self.lastfm.get_cover(artist,album)
		if album_uri == '':
			album_uri = self.defaultImg
		
		try:	
			a = StringIO.StringIO(urllib.urlopen(album_uri).read())
		except:
			print "error downloading file"
			print album_uri
			return (0)
			
		b = pygame.image.load(a)
		b = pygame.transform.scale(b,(280,280))
		
		# check cache again before we add image
		for i in range(len(self.cover_cache)):
                        if self.cover_cache[i][0] == artist:
                                artistID = i
                                for n in range(len(self.cover_cache[i][1])):
                                        if self.cover_cache[i][1][n][0] == album:
                                                return(0)
			
		if artistID != -1:
			self.cover_cache[artistID][1].append([album,album_uri,b])
			if len(self.cover_cache) > 500:
				self.cover_cache.pop(0)	
		else:
			self.cover_cache.append([artist,[[album,album_uri,b]]])
		
#		print "Added new image: " + album_uri + " / " + artist + " - " + album
#		print self.cover_cache
		if self.coverwait:
			self.update_cover()
		return(1)
	
	def update_coverqueue(self):
		if (self.playlist):
			self.cover_queue.put((1,[self.artist,self.album,self.title]))
			i=0
			while i <= 5 and i+self.plpos <= self.pllen-1:
				print (i+self.plpos)
				print (self.pllen-1)
				a = self.playlist[i+self.plpos]['artist']
				b = self.playlist[i+self.plpos]['album']
				c = self.playlist[i+self.plpos]['title']
				d = [a,b,c]
				print c
				self.cover_queue.put((1000+i+self.plpos,d))
				i = i + 1
			
								
	def update_mpd(self):
		print "Update MPD!"
		status = self.mpdutil.get_status()
		if status != 'DISCONNECTED':
			info 		= self.mpdutil.get_info()
			self.playlist 	= self.mpdutil.get_playlist()
			self.pllen 	= int(len(self.playlist))
			self.state 	= status['state']
			
			try:
				album = info['album'].decode('utf-8')
			except:
				album = 'None'
						
			try:
				title = info['title'].decode('utf-8')
			except:
				title = 'None'
										
			try:
				self.artist = info['artist'].decode('utf-8')
			except:
				self.artist = 'None'
			
			try:
				self.plpos = int(status['song'])
			except:
				self.plpos = -1
				
			if self.title != title:
				self.title = title
				self.updatetrack = True
			
			if self.album != album:
				self.album = album
				self.updatealbum = True
			
			self.check_updates();
			
		else:
			self.state="disconnected"
			
	def check_updates(self):
		if self.updatetrack:
			self.update_text()
			self.updatetrack=False
			self.updatecoverqueue=True
		
		if self.updatealbum:
			self.update_cover()
			self.updatealbum=False
			self.updatecoverqueue=True
			
		if self.updatecoverqueue:
			self.update_coverqueue()
			self.updatecoverqueue=False
			
	

	def mpd_thread(self):
		while 1:
			try:
				self.mpdutil.client.idle()
				self.update_mpd()
				sleep(2)
			except:
				a = self.mpdutil.connect()
				if a == 1:
					self.update_mpd()
					sleep(1)
				else:
					self.state = 'disconnected'
					sleep(3)
					
	def queue_thread(self):
		while True:
			item = self.cover_queue.get()
			self.get_cover(item[1])
			self.cover_queue.task_done()
					
					
	def loop_thread(self):
		while 1:
			self.update_LCD()									
			sleep(.3)
