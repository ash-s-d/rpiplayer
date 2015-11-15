#!/usr/bin/env python

"""playliststore.py: PlaylistStore generic class managing the playlist data storage."""

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

class PlaylistStore():

	storageType = "GENERIC"

	def __init__(self):
		ok = self.test()

		if not ok:
			raise Exception(self.storageType + " not ready!")

	def fetch(self):
		"""
		To be overridden when subclassed
		"""
		return ""

	def save(self, playlist):
		"""
		To be overridden when subclassed
		"""

	def flush(self):
		"""
		To be overridden when subclassed
		"""

	def test(self):
		"""
		To be overridden when subclassed
		"""
		return True