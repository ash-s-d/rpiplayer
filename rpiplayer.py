#!/usr/bin/env python

"""rpiplayer.py: 'Main', or point of entry, code for the video player wrapper for RaspberryPI."""

import argparse
import json

from ConfigParser import SafeConfigParser

from classes.playliststorememcache import PlaylistStoreMemcache
from classes.player import Player

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

def main():
	parser = argparse.ArgumentParser(description = "Video player wrapper for RaspberryPI.")

	parser.add_argument("--list", action='store_true', help = "List available files")
	parser.add_argument("--delete", help = "Delete provided file from repository")
	parser.add_argument("--play", help = "Play provided playlist")
	parser.add_argument("--stop", action='store_true', help = "Abort/stop player")
	parser.add_argument("--status", action='store_true', help = "Get status of player")

	args = parser.parse_args()

	if not (args.list or args.delete or args.play or args.stop or args.status):
		parser.error("At least one argument is expected.")	
	else:	
		configurations = SafeConfigParser()
		configurations.read("config.ini")

		playlistStore = PlaylistStoreMemcache	(
													configurations.get("Memcache", "Host"),
													configurations.get("Memcache", "Port")
												)

		player = Player (
							configurations.get("General", "SuperUserPrivilegesNeeded"),
							configurations.get("General", "FilesRepositoryAbsolutePath"),
							configurations.get("VideoPlayer", "Name"),
							configurations.get("VideoPlayer", "AbsolutePath"),
							configurations.get("VideoPlayer", "AdditionalArguments"),
							configurations.get("VideoUtility", "Name"),
							configurations.get("VideoUtility", "AbsolutePath"),
							configurations.get("VideoUtility", "AdditionalArguments"),
							playlistStore,
							configurations.get("Daemon", "PidFileAbsolutePath")
						)

		if (args.list):
			print player.list()
		elif (args.delete):
			print player.delete(args.delete)
		elif (args.play):
			print player.play(json.loads(args.play))
		elif (args.stop):
			print player.stop()
		else:
			print player.status()

if __name__ == "__main__":
   main()