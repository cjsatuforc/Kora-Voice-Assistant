import math

import adsk.cam
import adsk.core
import adsk.fusion

from ....kora_utils import getApp
from ..ExecutionStatusCodes import StatusCodes


def rotate(direction, magnitude=None, units='degrees'):
    try:
        app = getApp()
        if not direction:
            return StatusCodes.NONFATAL_ERROR
        if not units or units == 'degrees':
            if magnitude == None:
                magnitude = math.pi / 2.0
            else:
                magnitude = math.radians(magnitude)
            units = 'radians'
        elif magnitude == None:
            magnitude = math.pi / 2.0

        camera = app.activeViewport.camera
        rotationMatrix = adsk.core.Matrix3D.create()

        if direction == 'left' or direction == 'right':
            axisOfRotation = camera.upVector
            if direction == 'left':
                axisOfRotation.scaleBy(-1.0)
            rotationMatrix.setToRotation(magnitude, axisOfRotation, camera.target)
        else:
            axisOfRotation = camera.eye.asVector()
            axisOfRotation.normalize()
            axisRotationMatrix = adsk.core.Matrix3D.create()
            subAxis = camera.upVector
            if direction.startswith('up'):
                subAxis.scaleBy(-1.0)
            axisRotationMatrix.setToRotation(math.pi / 2.0, subAxis, camera.target)
            axisOfRotation.transformBy(axisRotationMatrix)
            rotationMatrix.setToRotation(magnitude, axisOfRotation, camera.target)
    
        newPos = camera.eye.asVector()
        newPos.transformBy(rotationMatrix)
        camera.eye = newPos.asPoint()

        newUpVector = camera.upVector.copy()
        newUpVector.transformBy(rotationMatrix)
        camera.upVector = newUpVector

        app.activeViewport.camera = camera

        return StatusCodes.SUCCESS
    except:
        return StatusCodes.NONFATAL_ERROR
