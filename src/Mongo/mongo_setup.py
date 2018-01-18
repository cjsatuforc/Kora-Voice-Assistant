import mongoengine

def globalInit():
    mongoengine.register_connection(alias='logs', name='kora')