#!/usr/bin/env python

"""message.py: Message class defining the output format for the player commands."""

import json

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

class Message:
	msg = None

	def __init__(self, operation, arguments, error, message, output):
		self.msg = 	{	
						'operation': operation,
						'arguments': arguments,
						'error': error,
						'message': message,
						'output': output
					}

	def getJson(self):
		return json.dumps	(
								self.msg,
								indent = 4, 
								# sort_keys = True,
								separators = (',', ': ')
							)
