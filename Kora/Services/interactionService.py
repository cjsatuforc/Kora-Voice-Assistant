# import mongoengine
from ..Mongo.Interaction import Interaction 
from ..Mongo import mongoSetup as mongoSetup

mongoSetup.globalInit() #connecting to db

def logInteraction(data):
	newInteraction = Interaction()

	if(data):
		if('user' in data):
			newInteraction.user = data['user']
		if('userCommand' in data):
			newInteraction.userCommand = data['userCommand']
		if('commandIntent' in data):
			newInteraction.commandIntent = data['commandIntent']
		if('context' in data):
			newInteraction.context = data['context']
		if('chosenAPICall' in data):
			newInteraction.chosenAPICall = data['chosenAPICall']
		if('fusionResponse' in data):
			newInteraction.fusionResponse = data['fusionResponse']
		if('execTime' in data):
			newInteraction.execTime = data['execTime']

	newInteraction.save()

def findUserInserts(userID):
    inserts = Interaction.objects(user=userID)
    return list(inserts)