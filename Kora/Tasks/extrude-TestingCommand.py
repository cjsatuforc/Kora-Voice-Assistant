import adsk.core, adsk.fusion, adsk.cam, traceback
from random import randint

ui  = None
amount = 0
commandId = None
commandName = 'Select a profile to extrude'
commandDescription = 'Select a profile to extrude'
# Global set of event handlers to keep them referenced for the duration of the command
handlers = []
	   
class MyCommandInputHandler(adsk.core.InputChangedEventHandler):
	def __init__(self):
		super().__init__()
	def notify(self, args):
		try:
			command = args.firingEvent.sender
			inputs = command.commandInputs

			# We need access to the inputs within a command during the execute.
			selectionInput = inputs.itemById(commandId + '_sel')
			sel = selectionInput.selection(0)
			if(sel and sel.isValid):
				command.doExecute(False)
				
		except:
			if ui:
				ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class MyExecuteHandler(adsk.core.CommandEventHandler):
	def __init__(self):
		super().__init__()
	def notify(self, args):
		try:
			command = args.firingEvent.sender
			inputs = command.commandInputs

			# We need access to the inputs within a command during the execute.
			selectionInput = inputs.itemById(commandId + '_sel')
			sel = selectionInput.selection(0)
			if(sel and sel.isValid):
				global amount
				extrudeSelect(sel.entity, amount)
		except:
			if ui:
				ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
	def __init__(self):
		super().__init__()
	def notify(self, args):
		try:
			for handle in handlers:
				del handle
			global ui
			cmdDef = ui.commandDefinitions.itemById(commandId)
			cmdDef.deleteMe()
		except:
			if ui:
				ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
				
				
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
	def __init__(self):
		super().__init__()
	def notify(self, args):
		try:
			cmd = args.command
			# Dont show OK button on dialog
			cmd.isOKButtonVisible = False

			onInputChange = MyCommandInputHandler()
			cmd.inputChanged.add(onInputChange)
			handlers.append(onInputChange)

			onExecute = MyExecuteHandler()
			cmd.execute.add(onExecute)
			handlers.append(onExecute)

			onDestroy = MyCommandDestroyHandler()
			cmd.destroy.add(onDestroy)
			handlers.append(onDestroy)

			inputs = cmd.commandInputs
			global commandId
			
			# Create tab input 1

			selectionInput = inputs.addSelectionInput(commandId + '_sel', 'Extrude Selection', 'Select a profile')
			selectionInput.addSelectionFilter('Profiles')
			selectionInput.setSelectionLimits(1)

		except:
			if ui:
				ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
				
def extrudeSelect(entity, amount):
	try:
		app = adsk.core.Application.get()
		# Get the current Document
		doc = app.documents.item(0)

		# Get the current Design
		product = app.activeProduct
		design = adsk.fusion.Design.cast(product)

		# Get the root component of the active design
		rootComp = design.rootComponent
				
		# Get extrude features
		extrudes = rootComp.features.extrudeFeatures   
		distance = adsk.core.ValueInput.createByReal(amount)
		
		extrude = extrudes.addSimple(entity, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation) 
		return 1
	except:
		return -1

def convertToCM(amnt, units):
	if units == 'centimeters':
		return amnt;
	elif units == 'milimeters':
		return (amnt / 10)
	elif units == 'meters':
		return (amnt * 100)
	elif units == 'inches':
		return (amnt * 2.54)
	elif units == 'feet':
		return (amnt * 30.48)

	return 0 # No match case	
	
def run(amnt, units='centimeters'):
	from ..kora_modules.fusion_execute_intent import executionStatusCodes
	"""
	Extrude can only take entities of type 'Profile'

	Problem to solve:
		1. Using a command dialog doesn't allow us to return a executionStatusCode.
		   The run() function simply calls cmdDef.execute() then returns and the 
		   command dialog runs in a seperate thread in the API (I'm guessing).
		   The point is, when using command dialog, the run function returns 
		   instantly, so we lose chance of returning a value. There should be a 
		   way to, but I haven't found it yet.
		2. Can't terminate the command from code. Meaning, after the user selects
		   a Profile to extrude, the command dialog should automatically kill itself,
		   but it doesn't and needs the user to click 'close.' which is a hassle.
	"""
	try:
		global commandId
		global commandName
		global commandDescription
		global amount
		global ui
		ui = adsk.core.Application.get().userInterface
		commandId = 'DialogExtrudeSelect' + str(randint(0,100000))
		ui.messageBox(commandId)
		
		amount = convertToCM(amnt, units)
		selections = ui.activeSelections
		found = False

		# If there are entities selected
		if selections:
			# For all enties, if they are of type Profile, extrude them
			for sel in selections.asArray():
				if sel and (sel.entity.classType() == adsk.fusion.Profile.classType()):
					found = True
					if extrudeSelect(sel.entity,amount) == -1:
						# If error in extrudeing, return error to log
						return executionStatusCodes.NONFATAL_ERROR
		# If no selections or no Profiles, ask user to select one
		if not found:
			# Create command defintion
			cmdDef = ui.commandDefinitions.itemById(commandId)
			if not cmdDef:
				cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription)
				
			# Add command created event
			onCommandCreated = MyCommandCreatedHandler()
			cmdDef.commandCreated.add(onCommandCreated)
			# Keep the handler referenced beyond this function
			handlers.append(onCommandCreated)

			# Execute command
			cmdDef.execute()
	except:
		if ui:
			ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
			return executionStatusCodes.FATAL_ERROR