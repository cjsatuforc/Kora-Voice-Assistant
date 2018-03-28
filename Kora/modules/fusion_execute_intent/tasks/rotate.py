import adsk.core, adsk.fusion, adsk.cam
import math

from ..ExecutionStatusCodes import StatusCodes
from ....kora_utils import getApp


def _rotate(direction, magnitude=None, units='degrees'):
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

    # TODO: fix vertical rotation of 90 degrees.
    if direction == 'left' or direction == 'right':
        axisOfRotation = camera.upVector
        if direction == 'left':
            axisOfRotation.y *= -1.0
        rotationMatrix.setToRotation(magnitude, axisOfRotation, camera.target)
    else:
        axisOfRotation = camera.eye.asVector()
        axisOfRotation.normalize()
        axisRotationMatrix = adsk.core.Matrix3D.create()
        if direction == 'up' or direction == 'upward':
            axisOfRotation.y *= -1.0
        subAxis = camera.upVector
        axisRotationMatrix.setToRotation(math.pi / 2.0, subAxis, camera.target)
        axisOfRotation.transformBy(axisRotationMatrix)
        rotationMatrix.setToRotation(magnitude, axisOfRotation, camera.target)

    newPos = camera.eye.asVector()
    newPos.transformBy(rotationMatrix)
    camera.eye = newPos.asPoint()
    app.activeViewport.camera = camera

    return StatusCodes.SUCCESS


def run(direction, magnitude=None, units='degrees'):
    return _rotate(direction, magnitude, units)
