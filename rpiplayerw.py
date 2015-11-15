#!/usr/bin/env python

"""rpiplayer.py: REST API for the video player wrapper for RaspberryPI."""

import cgi
import json
import re
import sys

from ConfigParser import SafeConfigParser

from classes.playliststorememcache import PlaylistStoreMemcache
from classes.player import Player

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

def application(env, start_response):
	output = ""
	error = False

	form = cgi.FieldStorage(
								fp = env['wsgi.input'],
								environ = env,
								keep_blank_values = True
							)

	# operation = form.getvalue('operation')
	queryStr = env['QUERY_STRING']

	match = re.match('^operation=(play|stop|status|list|upload|delete)(&file=(.*))?', queryStr)

	if match is None:
	# if operation not in ['play','stop','status', 'list', 'upload', 'delete']:
		error = True
	else:
		operation = match.group(1)

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

		if (env['REQUEST_METHOD'] == "GET"):
			if (operation == "list"):
				output = player.list()
			elif (operation == "status"):
				output = player.status()
			else:
				error = True
		elif (env['REQUEST_METHOD'] == "POST"): 
			if (operation == "play"):
				if getattr(form, "file"):
					jsonString = form.file.read()

					output = player.play(json.loads(jsonString))
				else:
					error = True
			elif (operation == "upload"):
				fileItem = form['new_file']

				if fileItem.filename:
					output = player.save(fileItem)
				else:
					error = True
			else:
				error = True
		elif (env['REQUEST_METHOD'] == "PUT"):
			if (operation == "stop"):
				output = player.stop()
			else:
				error = True
		elif (env['REQUEST_METHOD'] == "DELETE"):
			if (operation == "delete"):
				fileName = match.group(3)

				if fileName:
					output = player.delete(fileName)
				else:
					error = True
			else:
				error = True
		else:
			error = True

		if error:
			start_response("500 Internal Server Error", [("Content-Type", "text/html")])
		else:
			start_response	("200 OK", 	[
											("Access-Control-Allow-Origin", "*"),
											("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE"),
											("Access-Control-Allow-Headers", "x-requested-with"),
											("Content-Type", "application/json")
										]
							)

			return output
