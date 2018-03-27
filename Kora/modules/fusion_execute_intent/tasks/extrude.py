import adsk.core, adsk.fusion, adsk.cam, traceback

from ..ExecutionStatusCodes import StatusCodes

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

def convertToCM(amnt, units):
    if units == 'centimeters':
        return amnt;
    elif units == 'millimeters' or 'millimeter':
        return (amnt / 10)
    elif units == 'meters':
        return (amnt * 100)
    elif units == 'inches':
        return (amnt * 2.54)
    elif units == 'feet':
        return (amnt * 30.48)

    return 0


def run(amnt=1, units='centimeters'):
    try:
        supportedExtrusionTypes = {
            adsk.fusion.Profile.classType(),
            adsk.fusion.BRepFace.classType()
        }
        supportedSelectionFilters = 'Profiles,Faces'

        ui = adsk.core.Application.get().userInterface

        amount = convertToCM(amnt, units)
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
