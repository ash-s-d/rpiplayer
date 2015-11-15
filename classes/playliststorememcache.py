#!/usr/bin/env python

"""playliststorememcache.py: PlaylistStoreMemcache class, inherited from PlaylistStore, managing the playlist Memcache data storage."""

import json
import memcache
import socket

from classes.playliststore import PlaylistStore

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

class PlaylistStoreMemcache(PlaylistStore):

	storageType = "MEMCACHE"

	key = None
	cache = None

	def __init__(self, host, port):
		self.cache = memcache.Client(
										[host + ":" + port], 
										debug = 0
									)

		self.key = socket.gethostname() + "_playlist"

		PlaylistStore.__init__(self)

	def fetch(self):
		playlist = None

		playlistJson = self.cache.get(self.key) 

		if playlistJson is not None:
			playlist = json.loads(playlistJson)

		return playlist

	def save(self, playlist):
		self.cache.set(self.key, json.dumps(playlist))

	def flush(self):
		self.cache.delete(self.key)

	def test(self):
		working = False

		testKey = self.key + "_test"

		self.cache.set(testKey, "Testing if Memcache is actually working!")

		if self.cache.get(testKey) is not None:
			self.cache.delete(testKey)

			working = True

		return working
