import math

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from ....kora_utils import getApp, getUI
from ..ExecutionStatusCodes import StatusCodes


def extrudeSelect(entity, amount):
    try:
        app = getApp()

        # Get the current Design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        rootComp = design.rootComponent

        # Get extrude features
        extrudes = rootComp.features.extrudeFeatures
        distance = adsk.core.ValueInput.createByReal(amount)

        extrude = extrudes.addSimple(entity, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        if entity.classType() == adsk.fusion.BRepFace.classType():
            originalBody = entity.body
            toolBodies = adsk.core.ObjectCollection.create()
            toolBodies.add(originalBody)
            targetBody = extrude.bodies.item(0)
            combineFeaturesInput = rootComp.features.combineFeatures.createInput(targetBody, toolBodies)
            rootComp.features.combineFeatures.add(combineFeaturesInput)

        return 1
    except:
        return -1


def convertToCM(magnitude, units):
    if units == 'centimeters' or 'centimeter':
        return magnitude;
    elif units == 'millimeters' or 'millimeter':
	    return (magnitude / 10)
    elif units == 'meters' or 'meter':
        return (magnitude * 100)
    elif units == 'inches' or 'inch':
        return (magnitude * 2.54)
    elif units == 'feet' or 'foot':
        return (magnitude * 30.48)
        
    return 0 # No match case


def extrude(text, magnitude=1, units='centimeters'):
    ui = None
    try:
        ui = getUI()

        if not magnitude or math.isnan(magnitude):
            return StatusCodes.NONFATAL_ERROR
         # if amount should be negative
        if text and ("push down" in text or "negative" in text) and magnitude > 0:
            magnitude = magnitude * -1

        if magnitude is None:
            return StatusCodes.NONFATAL_ERROR

        supportedExtrusionTypes = {
            adsk.fusion.Profile.classType(),
            adsk.fusion.BRepFace.classType()
        }

        supportedSelectionFilters = 'Profiles,Faces'

        amount = convertToCM(magnitude, units)
        selections = ui.activeSelections
        found = False

        if selections:
            for sel in selections.asArray():
                if sel and sel.entity.classType() in supportedExtrusionTypes:
                    found = True
                    extrudeResult = extrudeSelect(sel.entity, amount)
                    if extrudeResult == -1:
                        return StatusCodes.NONFATAL_ERROR
        # If no supported extrude types in selection, ask user to select one
        if not found:
            ui.messageBox("Select a profile or face to extrude.")
            selectedSurface = ui.selectEntity('Select something to extrude.', supportedSelectionFilters)
            extrudeResult = extrudeSelect(selectedSurface.entity, amount)
            if extrudeResult == -1:
                return StatusCodes.NONFATAL_ERROR

        return StatusCodes.SUCCESS
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            return StatusCodes.FATAL_ERROR
