from ..packages.mongoPackages import mongoengine

def globalInit():
    mongoengine.register_connection(alias='core', name='kora')
    mycon = mongoengine.connect('kora', 'core', host='localhost')