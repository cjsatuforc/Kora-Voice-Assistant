from functools import wraps
import time


import adsk.core, adsk.fusion, adsk.cam, traceback
_app = adsk.core.Application.get()
_ui = _app.userInterface

from ..Mongo.Interaction import Interaction 
from ..Mongo import mongoSetup as mongoSetup
from ..Services import debug

mongoSetup.globalInit() #connecting to db

def logInteraction():
	def decorator(executeFusion):
		@wraps(executeFusion)
		def wrapper(*args, **kwargs):
			try:
				# extract the dictionary from *args
				argToFusion = args[0]
				if debug.on:
					#if debug, skip the logging
					executeResponse = executeFusion(*args, **kwargs)

				else:
					#get new Interaction object
					newInteraction = Interaction()

					if 'user' in argToFusion:
						newInteraction.user = argToFusion['user']
						del argToFusion['user'] #take it out to store pure witResponse

					#Gather the time it took wit to respond
					totalExecuteTime = 0
					if 'witStreamTime' in argToFusion:
						totalExecuteTime += float(argToFusion['witStreamTime'])
						del argToFusion['witStreamTime'] #take it out to store pure witResponse
						
					#Store the wit response free of added JSON
					newInteraction.witResponse = argToFusion

					#Time Fuison execute command
					before = time.time()
					
					executeResponse = executeFusion(*args, **kwargs)
					
					after = time.time()
					
					#Store total execution time
					totalExecuteTime += float(after - before)
					newInteraction.execTime = totalExecuteTime

					#Extract from executeResponse
					if 'chosenAPICall'in executeResponse:
						newInteraction.chosenAPICall = executeResponse['chosenAPICall']
					if 'fusionExecutionStatus' in executeResponse:
						newInteraction.fusionExecutionStatus = executeResponse['fusionExecutionStatus']
				
					try:
						newInteraction.save()
					except:
						_ui.messageBox('InteractionService Failed to Save'.format(traceback.format_exc()))

				#return the execution status like originally
				return executeResponse['fusionExecutionStatus']
			except:
				NONFATAL_ERROR = 2
				return NONFATAL_ERROR

		return wrapper
	return decorator