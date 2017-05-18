import time
import pylast
import os.path

API_KEY = 'f6860b7bfbe6171594899035a3040ca7'
API_SECRET = 'b5f5f0499b1a9d2f6217973ce106d2df'
username = "asdfrewqt"
password_hash = pylast.md5("bollocks")
libDir = "/mnt/library/"


class LastfmFrontend():
	def __init__(self):
		self.lastfm = None

	def process_title(album):
		album = album.split(' ')
		album = string.join(album,'+')
		album = album.replace(':','')
		album = album.replace('/', '+')
		return album	
		
	def connect(self):
		try:
			#self.network = lastfm.Api(API_KEY)
			self.network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET, username = username, password_hash = password_hash)
            		print('Connected to Last.fm')
        	except:
            		print('Error during Last.fm setup')
	
	def get_cover (self, artist, album):
		#filesystem
		try:
			localFile = libDir + artist + "/" + album + "/folder.jpg"
			if os.path.isfile(localFile) == True:
				return localFile
			
		except:
			print ("Error getting cover from Local") 

		# LASTFM
		try:
			lfmAlbum = self.network.get_album(artist,album)
			album_uri= lfmAlbum.get_cover_image(size=3)
			if album_uri:
				return album_uri

		except:
			print ("Error getting cover from LastFM")

		return ''
