#!/usr/bin/env python

"""rpiplayerd.py: 'Main', or point of entry, code for the video player wrapper daemon for RaspberryPI."""

import argparse

from ConfigParser import SafeConfigParser

from classes.playliststorememcache import PlaylistStoreMemcache
from classes.playerdaemon import PlayerDaemon

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

def main():
	parser = argparse.ArgumentParser(description = "Video player wrapper daemon for RaspberryPI.")

	parser.add_argument("--start", action='store_true', help = "Start daemon")
	parser.add_argument("--stop", action='store_true', help = "Abort/stop daemon")
	parser.add_argument("--restart", action='store_true', help = "Restart daemon")

	args = parser.parse_args()

	if not (args.start or args.stop or args.restart):
		parser.error("At least one argument is expected.")	
	else:	
		configurations = SafeConfigParser()
		configurations.read("config.ini")

		playlistStore = PlaylistStoreMemcache	(
													configurations.get("Memcache", "Host"),
													configurations.get("Memcache", "Port")
												)

		daemon = PlayerDaemon 	(
									configurations.get("Daemon", "PidFileAbsolutePath"),
									configurations.get("General", "FilesRepositoryAbsolutePath"),
									configurations.get("VideoPlayer", "Name"),
									configurations.get("VideoPlayer", "AbsolutePath"),
									configurations.get("VideoPlayer", "AdditionalArguments"),
									playlistStore,
									configurations.get("UDPAlivePackets", "Enabled"),
									int(configurations.get("UDPAlivePackets", "Interval")),
									int(configurations.get("UDPAlivePackets", "Port"))
								)

		if (args.start):
			daemon.start()
		elif (args.stop):
			daemon.stop()
		else:
			daemon.restart()

if __name__ == "__main__":
   main()