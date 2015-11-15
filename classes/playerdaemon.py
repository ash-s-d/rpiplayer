#!/usr/bin/env python

"""playerdaemon.py: PlayerDaemon class, inherited from Daemon, defining the player logic for the daemon."""

import os
import os.path
import re
import operator
import socket
import subprocess
import time

import psutil

from classes.daemon import Daemon
from classes.playliststorememcache import PlaylistStoreMemcache

from classes.utilities import Utilities

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

class PlayerDaemon(Daemon):

	filesRepoAbsPath = None

	playerName = None
	playerAbsPath = None
	playerArgs = None

	playlistStore = None

	uDPAlivePacketsEnabled = None
	uDPAlivePacketsInterval = None
	uDPAlivePacketsPort = None
	uDPAlivePacketsBroadcastAddr = None
	
	def __init__(self, pidFileAbsPath, filesRepoAbsPath, playerName, playerAbsPath, playerArgs, playlistStore, uDPAlivePacketsEnabled, uDPAlivePacketsInterval, uDPAlivePacketsPort):
		Daemon.__init__(self, pidFileAbsPath)
		
		self.filesRepoAbsPath = filesRepoAbsPath

		self.playerName = playerName
		self.playerAbsPath = playerAbsPath
		self.playerArgs = playerArgs

		self.playlistStore = playlistStore

		self.uDPAlivePacketsEnabled = uDPAlivePacketsEnabled
		self.uDPAlivePacketsInterval = uDPAlivePacketsInterval
		self.uDPAlivePacketsPort = uDPAlivePacketsPort
		self.uDPAlivePacketsBroadcastAddr = self.getBroadcastAddress()

	def run(self):
		while True:
			proc = Utilities.getProc(self.playerName)

			playlist = self.playlistStore.fetch()

			if proc is None:
				if playlist is not None:
					position = playlist['now_playing_position']

					play = True
				
					if (position >= len(playlist['files'])):
						if playlist['loop']:
							position = 0
						else:
							play = False

					if play:
						fileAbsFilePath = os.path.join(self.filesRepoAbsPath, playlist['files'][position]['name'])

						if(os.path.exists(fileAbsFilePath)):
							subprocess.call(
												self.playerAbsPath + " " +
												self.playerArgs + " " +
												fileAbsFilePath + " " +
												"&", 
												shell=True
											)

						position += 1

						playlist['now_playing_position'] = position
						
						self.playlistStore.save(playlist)
			elif playlist is None:
				Utilities.killProc(self.playerName)

			if self.uDPAlivePacketsEnabled:
				epoch = round(time.time())

				if epoch % self.uDPAlivePacketsInterval == 0:
					self.sendAlivePacket()

			time.sleep(1)

	def delpid(self):
		self.playlistStore.flush()

		Utilities.killProc(self.playerName)

		Daemon.delpid(self)

	def sendAlivePacket(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.sendto(
						"RPI Player '" + socket.gethostname() + "' is online!", 
						(self.uDPAlivePacketsBroadcastAddr, self.uDPAlivePacketsPort)
					)

	def getBroadcastAddress(self):
		broadcastAddress = subprocess.check_output	(
														"ip -o addr show | grep -w inet | grep -e eth | cut -d\  -f 9",
														shell = True
													)

		return broadcastAddress
