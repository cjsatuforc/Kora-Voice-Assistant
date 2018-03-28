
class StatusCodes(object):
    FATAL_ERROR = 'fatalError'  # For runtime errors/exceptions
    NONFATAL_ERROR = 'nonfatalError'  # For non-exception errors that make it so that execution can't be completed
    UNRECOGNIZED_COMMAND = 'unrecognizedCommand'  # Didn't recognize intent of command
    USER_ABORT = 'userAbort'  # User aborted command
    SUCCESS = 'success'