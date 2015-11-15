#!/usr/bin/env python

"""utilities.py: Utilities static class."""

import datetime
import operator
import re
import time

import psutil

__author__ = "Ashvin Domah"
__copyright__ = "Copyright 2014, Accenture Mauritius"
__maintainer__ = "Ashvin Domah"
__email__ = "ashvin.domah@accenture.com"
__status__ = "Production"
__version__ = "1.0"

class Utilities():

	@staticmethod
	def killProc(name):
		killed = False

		proc = Utilities.getProc(name)

		if proc is not None:
			p = psutil.Process(proc.pid)

			p.terminate()

			time.sleep(1)

			killed = Utilities.getProc(name) is None
		else:
			killed = True

		return killed

	@staticmethod
	def getProc(name):
		proc = None
		
		processes = sorted	(
								list(psutil.process_iter()), 
								key = operator.attrgetter('create_time'), 
								reverse = True
							)

		found = False
		counter = 0

		while not found and counter < len(processes):
			aProc = processes[counter]

			if aProc is not None:
				try:
					aProcName = aProc.name

					match = re.match(name, aProcName)

					if match is not None:
						proc = aProc				
						found = True
				except:
					pass

			counter += 1

		return proc

	@staticmethod
	def getDurationInSecsFromStrRep(durationStrRep):
		t = time.strptime(durationStrRep, '%H:%M:%S')

		return datetime.timedelta(hours = t.tm_hour, minutes = t.tm_min, seconds = t.tm_sec).total_seconds()

	@staticmethod
	def getDurationInStrRepFromSecs(durationSecs):
		return datetime.datetime.fromtimestamp(durationSecs).strftime("%H:%M:%S")