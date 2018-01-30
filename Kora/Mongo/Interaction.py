import mongoengine
import datetime

class Interaction(mongoengine.Document):
    postingDate    = mongoengine.DateTimeField(default=datetime.datetime.now)
    user           = mongoengine.UUIDField(required=True)
    userCommand    = mongoengine.StringField()
    commandIntent  = mongoengine.StringField()
    context        = mongoengine.DictField()
    chosenAPICall  = mongoengine.StringField()
    fusionResponse = mongoengine.DictField()
    execTime       = mongoengine.DecimalField(min_value=0.00)
    
    meta = {
        'db_alias': 'core',
        'collection': 'interaction'
    }