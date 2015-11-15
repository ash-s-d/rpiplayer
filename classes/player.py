#!/usr/bin/env python

"""player.py: Player class defining all the video player logic."""

import datetime
import json
import operator
import os
import os.path
import re
import subprocess
import sys
import time

import memcache
import psutil

from classes.message import Message
from classes.playliststorememcache import PlaylistStoreMemcache

from classes.utilities import Utilities

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

class Player:
	superUserPrivReq = None
	filesRepoAbsPath = None

	playerName = None
	playerAbsPath = None
	playerArgs = None
	
	utilName = None
	utilAbsPath = None
	utilArgs = None

	playlistStore = None

	daemonPidFileAbsPath = None
	
	def __init__(self, superUserPrivReq, filesRepoAbsPath, playerName, playerAbsPath, playerArgs, utilName, utilAbsPath, utilArgs, playlistStore, daemonPidFileAbsPath):
		os.environ['TZ'] = time.strftime("%Z", time.gmtime())

		self.superUserPrivReq = superUserPrivReq
		self.filesRepoAbsPath = filesRepoAbsPath

		self.playerName = playerName
		self.playerAbsPath = playerAbsPath
		self.playerArgs = playerArgs

		self.utilName = utilName
		self.utilAbsPath = utilAbsPath
		self.utilArgs = utilArgs

		self.playlistStore = playlistStore

		self.daemonPidFileAbsPath = daemonPidFileAbsPath

	def list(self):
		msg = None
		
		oper = "List files in repository '" + self.filesRepoAbsPath + "'."

		if(os.path.exists(self.filesRepoAbsPath)):
			msg =  Message	(
								oper,
								None,
								False,
								None,
								{
									'repository': self.filesRepoAbsPath,
									'free_space': self.getAvailableStorageSpace(),
									'contents': self.listFilesRecursively(self.filesRepoAbsPath)
								}
							)
		else:
			msg =  Message	(
								oper,
								None,
								True,
								"Directory '" + self.filesRepoAbsPath + "' doest not exist.",
								None
							) 

		return msg.getJson()

	def save(self, fileItem):
		error = False
		errorMsg = None

		fileName = os.path.basename(fileItem.filename)
		
		oper = "Upload of new file '" + fileName + "' in repository '" + self.filesRepoAbsPath + "'."

		try:
			open(os.path.join(self.filesRepoAbsPath, fileName), "wb").write(fileItem.file.read())
		except:
			error = True
			errorMsg = str(sys.exc_info()[1])

		return Message	(
							oper,
							None,
							error,
							errorMsg if error else None,
							None
						).getJson()

	def delete(self, fileName):
		error = False
		errorMsg = None

		oper = "Delete file '" + fileName + "' from repository '" + self.filesRepoAbsPath + "'."

		try:
			os.remove(os.path.join(self.filesRepoAbsPath, fileName))
		except:
			error = True
			errorMsg = str(sys.exc_info()[1])

		return Message	(
							oper,
							None,
							error,
							errorMsg if error else None,
							None
						).getJson()

	def play(self, playlist):
		error = False
		errorMsg = None

		plCpy = playlist.copy()

		oper = "Play new playlist."

		playerProc = Utilities.getProc(self.playerName)

		if playerProc is not None:
			error = True
			errorMsg = "Player is already running."
		else:
			subprocess.call(
								("sudo " if self.superUserPrivReq else "") + " " +
								"sh -c \"TERM=linux setterm -foreground black -clear > /dev/tty0\"", 
								shell=True
							)

			playlist['now_playing_position'] = 0
			playlist['received_date'] = datetime.datetime.fromtimestamp(time.time()).strftime("%d/%m/%Y %H:%M:%S")

			self.playlistStore.save(playlist)

			time.sleep(1.5)

			playerProc = Utilities.getProc(self.playerName)

			if playerProc is None:
				error = True
				errorMsg = "Playlist cannot be read for unknown reasons."

		return Message	(
							oper,
							plCpy,
							error,
							errorMsg if error else None,
							None
						).getJson() 

	def stop(self):
		error = False
		errorMsg = None

		oper = "Stop player."

		self.playlistStore.flush()

		time.sleep(1.5)

		stopped = Utilities.getProc(self.playerName) is None

		if not stopped:
			error = True
			errorMsg = "Cannot stop player for unknown reasons."

		return Message	(
							oper,
							None,
							error,
							errorMsg if error else None,
							None
						).getJson() 

	def status(self):
		oper = "Get player status."

		status = 	{
						'playlist': None,
						'status': None,
						'currently_playing_file': None,
						'currently_playing_total_time': None,
						'currently_playing_remaining_time': None
					}

		playerProc = Utilities.getProc(self.playerName)

		if playerProc is not None:
			playlist = self.playlistStore.fetch()

			playingFileIdx = playlist['now_playing_position'] - 1

			status['playlist'] = playlist
			status['status'] = "Running"
			status['currently_playing_file'] = playlist['files'][playingFileIdx]['name']

			totalTime = self.getVideoDuration(playingFileIdx)
			elapsedTime = time.time() - playerProc.create_time
			remainingTime = totalTime - elapsedTime

			status['currently_playing_total_time'] = Utilities.getDurationInStrRepFromSecs(totalTime)
			status['currently_playing_remaining_time'] = Utilities.getDurationInStrRepFromSecs	(
																									remainingTime if remainingTime > 0 else 0
																								)
		else:
			status['status'] = "Idle" if self.isDaemonRunning() else "Stopped"

		return Message	(
							oper,
							None,
							False,
							None,
							status
						).getJson()	
		
	def listFilesRecursively(self, absPath):		
		f = []

		files = os.listdir(absPath)

		for index in range(len(files)):
			fileName = files[index]
			fileAbsPath = os.path.join(absPath, fileName)

			if(os.path.isdir(fileAbsPath)):
				f.append({'type': 'directory', 'name': fileName, 'files': self.listFilesRecursively(fileAbsPath)})
			else:
				f.append({'type': 'file', 'name': fileName, 'size': os.path.getsize(fileAbsPath)})

		return f

	def getPlaylistTotalDuration(self):
		totalDuration = 0

		playlist = playliststorememcache.fetch()

		for i in range(0, len(playlist['files']) - 1):
			totalDuration += getVideoDuration(i)

		return totalDuration

	def getVideoDuration(self, playlistIndex):
		playlist = self.playlistStore.fetch();

		video = playlist['files'][playlistIndex]

		durationInStrRep = video['duration']

		if not durationInStrRep:
			videoFileAbsPath = os.path.join(self.filesRepoAbsPath, video['name'])

			durationStr = subprocess.check_output	(
														("sudo " if self.superUserPrivReq else "") + self.utilAbsPath + " " +
														self.utilArgs + " " +
														videoFileAbsPath + " " +
														"2>&1 | grep Duration: | cut -d ' ' -f 4 | sed s/\.[0-9]*,//",
														shell = True
													)

			durationInStrRep = durationStr.strip()

			playlist['files'][playlistIndex]['duration'] = durationInStrRep

			self.playlistStore.save(playlist)
							 
		return Utilities.getDurationInSecsFromStrRep(durationInStrRep)

	def getAvailableStorageSpace(self):
		spaceInKBStrRep = subprocess.check_output	(
														("sudo " if self.superUserPrivReq else "") + " " +
														"df -P " + 
														self.filesRepoAbsPath + " " +
														"| tail -1 | cut -d' ' -f 1 | xargs df -k | sed -e /Filesystem/d | tr -s ' ' | cut -d ' ' -f 4",
														shell = True
													)

		return int(spaceInKBStrRep)*1024

	def isDaemonRunning(self):
		running = False

		if(os.path.exists(self.daemonPidFileAbsPath)): 
			pidFileContent = ""

			with open(self.daemonPidFileAbsPath, 'r') as content:
				pidFileContent = content.read().strip()

			running = psutil.Process(int(pidFileContent)) is not None

		return running
