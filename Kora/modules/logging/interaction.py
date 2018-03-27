import datetime

from ...ext.mongoPackages import mongoengine

# class Interaction(mongoengine.Document):
#     postingDate         = mongoengine.DateTimeField(default=datetime.datetime.now)
#     user                = mongoengine.StringField(required=True)
#     userCommand         = mongoengine.StringField()
#     intentConfidence    = mongoengine.StringField()
#     commandIntent       = mongoengine.StringField()
#     context             = mongoengine.DictField()
#     chosenAPICall       = mongoengine.StringField()
#     fusionResponse      = mongoengine.DictField()
    # execTime            = mongoengine.DecimalField(min_value=0.00)
    
#     meta = {
#         'db_alias': 'core',
#         'collection': 'interaction'
#     }

class Interaction(mongoengine.Document):
    postingDate             = mongoengine.DateTimeField(default=datetime.datetime.now)
    user                    = mongoengine.StringField(required=True)
    witResponse             = mongoengine.DynamicField()
    chosenAPICall           = mongoengine.StringField()
    fusionExecutionStatus   = mongoengine.IntField()
    execTime                = mongoengine.DecimalField(min_value=0.00)
    
    meta = {
        'db_alias': 'core',
        'collection': 'interaction'
    }