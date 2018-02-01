from ..packages.mongoPackages import mongoengine

def globalInit():
    mongoengine.register_connection(alias='core', name='kora')
    mongoengine.connect('kora', 'core', host='localhost')