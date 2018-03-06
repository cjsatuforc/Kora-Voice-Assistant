import adsk.core, adsk.fusion, adsk.cam, traceback
import math

##
##   * Rotates the camera <magnitude> units in the <direction>
##
def _rotate(direction, magnitude=None, units='degrees'):
	# Put here to avoid circular dependencies. If put in global space, import error
	from ..kora_modules.fusion_execute_intent import executionStatusCodes
	_app = adsk.core.Application.get()

	if not direction:
		return executionStatusCodes.NONFATAL_ERROR
	if units == 'degrees':
		if magnitude == None:
			magnitude = math.pi / 2.0
		else:
			magnitude = math.radians(magnitude)
		units = 'radians'
	elif magnitude == None:
		magnitude = math.pi / 2.0

	camera = _app.activeViewport.camera
	rotationMatrix = adsk.core.Matrix3D.create()

	#TODO: I've been messing around with how to make rotation work properly and am almost there.
	#TODO: Will continue to work on it with new method of not actually rotating but moving camera which in turn rotates object. -Austin
	if direction == 'left' or direction == 'right':
		"""axisOfRotation = camera.eye.asVector()
		if direction == 'right':
			axisOfRotation.scaleBy(-1.0)
		translationVector = camera.upVector
		rotationMatrix.setToRotation(math.pi / 2.0, axisOfRotation, camera.target)
		translationVector.transformBy(rotationMatrix)
		magnitude = abs(magnitude) / math.pi
		translationVector.scaleBy(magnitude*100)
		newPos = camera.eye.asVector()
		newPos.add(translationVector)
		camera.eye = newPos.asPoint()
		"""
		if direction == 'left':
			axisOfRotation = camera.upVector
			axisOfRotation.y *= -1.0
		elif direction == 'right':
			axisOfRotation = camera.upVector
		rotationMatrix.setToRotation(magnitude, axisOfRotation, camera.target)
		newPos = camera.eye.asVector()
		newPos.transformBy(rotationMatrix)
		camera.eye = newPos.asPoint()
	else:
		"""if magnitude < 0:
			direction = 'up' if direction == 'down' or direction == 'downward' else 'down'
		magnitude = abs(magnitude) / math.pi
		if direction == 'down' or direction == 'downward':
			magnitude *= -1.0
		translationVector = camera.upVector
		translationVector.scaleBy(magnitude*100)
		newPos = camera.eye.asVector()
		newPos.add(translationVector)
		camera.eye = newPos.asPoint()
		"""
		axisOfRotation = camera.eye.asVector()
		axisOfRotation.normalize()
		axisRotationMatrix = adsk.core.Matrix3D.create()
		if direction == 'up' or direction == 'upward':
			subAxis = camera.upVector
			axisOfRotation.y *= -1.0
		else:
			subAxis = camera.upVector
		axisRotationMatrix.setToRotation(math.pi / 2.0, subAxis, camera.target)
		axisOfRotation.transformBy(axisRotationMatrix)


	_app.activeViewport.camera = camera

	return executionStatusCodes.SUCCESS


def run(direction, magnitude=None, units='degrees'):
	return _rotate(direction, magnitude, units)