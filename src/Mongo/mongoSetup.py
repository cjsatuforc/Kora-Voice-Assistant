import mongoengine

def globalInit():
    mongoengine.register_connection(alias='core', name='kora')
    # mongoengine.connect(db='kora', host='mongodb://localhost/kora', )
    mongoengine.connect('kora', 'core', host='localhost')