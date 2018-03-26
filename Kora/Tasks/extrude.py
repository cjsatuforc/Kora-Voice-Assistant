import adsk.core, adsk.fusion, adsk.cam, traceback

from .ExecutionStatusCodes import StatusCodes

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
    elif units == 'millimeters' or 'millimeter':
        return (amnt / 10)
    elif units == 'meters':
        return (amnt * 100)
    elif units == 'inches':
        return (amnt * 2.54)
    elif units == 'feet':
        return (amnt * 30.48)

    return 0  # No match case


def run(amnt=1, units='centimeters'):
    """
    Extrude can only take entities of type 'Profile'
    """
    try:
        ui = adsk.core.Application.get().userInterface

        amount = convertToCM(amnt, units)
        selections = ui.activeSelections
        found = False

        # If there are entities selected
        if selections:
            # For all enties, if they are of type Profile, extrude them
            for sel in selections.asArray():
                if sel and (sel.entity.classType() == adsk.fusion.Profile.classType()):
                    found = True
                    if extrudeSelect(sel.entity, amount) == -1:
                        # If error in extrudeing, return error to log
                        return StatusCodes.NONFATAL_ERROR
        # If no selections or no Profiles, ask user to select one
        if not found:
            ui.messageBox("Select a Profile To extrude")
            selectedSurface = ui.selectEntity('Select a Profile to extrude', 'Profiles')
            if extrudeSelect(selectedSurface.entity, amount) == -1:
                # If error in extrudeing, return error to log
                return StatusCodes.NONFATAL_ERROR

        return StatusCodes.SUCCESS

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            return StatusCodes.FATAL_ERROR
