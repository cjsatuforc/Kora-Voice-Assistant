import datetime

from ....ext.mongoPackages import mongoengine

class Interaction(mongoengine.Document):
    postingDate             = mongoengine.DateTimeField(default=datetime.datetime.now)
    user                    = mongoengine.StringField(required=True)
    witResponse             = mongoengine.DynamicField()
    chosenAPICall           = mongoengine.StringField()
    fusionExecutionStatus   = mongoengine.StringField()
    execTime                = mongoengine.DecimalField(min_value=0.00)
    
    meta = {
        'db_alias': 'core',
        'collection': 'interaction'
    }