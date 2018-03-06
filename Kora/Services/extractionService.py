def _getFromCommand(distilledCommand, searchKey):
    """
    :param distilledCommand: A dictionary containing command data.
    :param searchKey: A list of keys that indicate what should be found in command.
                        Ex- searchKey=['intent'] Return the value of the first key found in distilledCommand that is 'intent'
                        Ex- searchKey=['rotationQuantity', 'units'] Return the value of the first key that is 'units' that is nested inside of the value of key 'rotationQuantity'
    :return: The value of the specified key in distilledCommand
    """

    if not isinstance(searchKey, list):
        searchKey = [searchKey]

    def _find(cmd, sKey):
        if not sKey:
            if isinstance(cmd, dict) and 'value' in cmd:
                return cmd['value']
            return cmd
        elif not isinstance(cmd, dict):
            return None

        for key, value in cmd.items():
            nextCmd = value
            if key == sKey[0]:
                nextSKey = sKey[1:]
            else:
                nextSKey = sKey

            if isinstance(nextCmd, list):
                nextCmd = {i:nextCmd[i] for i in range(len(nextCmd))}

            res = _find(nextCmd, nextSKey)
            if not res is None:
                return res

        return None

    return _find(distilledCommand, searchKey)
