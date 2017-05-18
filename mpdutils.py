import logging
import time
from mpd import MPDClient

### MPD CONF
MPD_HOST = "192.168.2.10"
MPD_PORT = 6600

class MPDClientFrontend():
        def __init__(self):
                self.client = None

        def connect(self):
                try:
			self.client = MPDClient()
			#self.client.timeout = 20
			#self.client.idletimeout = 100
			self.client.connect(MPD_HOST, MPD_PORT)
			print('mpd connected. Version: ' + self.client.mpd_version)
			return 1
                except:
                        print('Error connecting to MPD.')
			return 0

	def get_status(self):
		try:
			i = self.client.status()	
        		return i
		except:
			i = 'DISCONNECTED'
			print('Error returning MPD status')
			return i
	def get_info(self):
		try:
			i = self.client.currentsong()
			return i
		except:
			i = ''
			print ('Error returning MPD info')
			return i

        def get_playlist(self):
                try:
                        i = self.client.playlistinfo()
                        return i
                except:
                        i = ''
                        print ('Error returning MPD info')
                        return i

	def send_cmd(self,cmd):
		try:
			self.client.send_noidle()
			if cmd == "play":
				self.client.pause()
			elif cmd == "stop":
				self.client.stop()
			elif cmd == "prev":
				self.client.previous()
			elif cmd == "next":
				self.client.next()
		except:
			print ("Error sending MPD cmd")
