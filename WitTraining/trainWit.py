from random import randint
import random

from witAutoTrainer import train, Entity, TrainingPhrase

class EntityTypes():
    rotation_quantity = 'rotation_quantity'
    extrude_quantity = 'extrude_quantity'
    units = 'units'
    direction = 'direction'
    fileName = 'file_name'

    # IMPORTANT: for wit builtin types like 'wit/number', just put whatever comes after 'wit/' e.g. 'number'
    #            Also, don't have any custom entities that collide with these e.g. don't have a custom 'number' entity
    wit_number = 'number'

class Intents():
    rotate = 'rotate'
    save = 'save'
    saveAs = 'save_as'
    extrude = 'extrude'

def getLoginCreds():
    # Change this to match whatever you need to get your personal loginCreds
    loginCredentials = None
    with open('./trainingConfig', 'r') as f:
        data = [_.strip() for _ in f.read().splitlines()]
        loginCredentials = {'username': data[0], 'password': data[1]}
    return loginCredentials

def generateTrainingPhrases():
    for phrase in RandomRotate(10):
        yield phrase
    for phrase in RandomExtrude(100):
        yield phrase
    for phrase in RandomSave(50):
        yield phrase
    for phrase in RandomSaveAs(50):
	        yield phrase

###############################
##                           ##
##     Phrase Generators     ##
##                           ##
###############################
def RandomSave(numToGenerate):
    while numToGenerate:
        # random.choice(['', 'please ']) + 'save ' +  random.choice(['', 'this', 'it', 'now']))
        yield TrainingPhrase(Intents.save, "please save this")
            
       
        numToGenerate -= 1


def RandomSaveAs(numToGenerate):
    while numToGenerate:
        version = random.choice(['one','two','three','four','five','six','seven','eight','nine','ten'])

        fileName = random.choice(['my draft', 'version', 'auto desk', 'chair', 'test', 
                                     'demo', 'auto desk demo']) \
                    + random.choice(['', ' ' + version])  
        fileName = Entity(fileName, EntityTypes.fileName)

        yield TrainingPhrase(Intents.saveAs, 
                random.choice(['', 'please ']) + 'save ' +  random.choice(['', 'this ', 'it ']) + 'as' + fileName)

        numToGenerate -= 1    


def RandomExtrude(numToGenerate):
    while numToGenerate:
        magnitude = random.random() * randint(0, 360)
        magnitude = round(magnitude, 2)
        makeInt = randint(0,1)  # 50% chance of getting an int
        if makeInt:
            magnitude = int(magnitude)
        makeInt = randint(0,10)  # 30% chance being negative (into page)
        if makeInt <= 3:
            magnitude = magnitude * -1
        
        units = random.choice(['millimeters', 'centimeters', 'meters', 'inches','feet'])

        magnitude = Entity(magnitude, EntityTypes.wit_number)
        units = Entity(units, EntityTypes.units)

        yield TrainingPhrase(Intents.extrude, random.choice(['pull up ', 'push down ', 'extrude ', 'extra rude', 'screwed']) + 
                    Entity(random.choice([
                        random.choice(['', 'by ']) + magnitude + units
                    ]), EntityTypes.extrude_quantity))

        numToGenerate -= 1


def RandomRotate(numToGenerate):
    while numToGenerate:
        magnitude = round(random.random() * randint(0, 360), 2)
        makeInt = randint(0,9)  # 90% chance of getting an int
        if makeInt:
            magnitude = int(magnitude)

        units = random.choice(['degrees'])
        direction = random.choice(['left', 'right', 'up', 'down', 'upward', 'upwards', 'downward', 'downwards'])

        magnitude = Entity(magnitude, EntityTypes.wit_number)
        units = Entity(units, EntityTypes.units)
        direction = Entity(direction, EntityTypes.direction)

        yield TrainingPhrase(Intents.rotate, 'rotate' +
                    Entity(random.choice([
                        magnitude + units + direction,
                        direction + random.choice(['', 'by']) + magnitude + units,
                        magnitude + direction,
                        direction + magnitude
                    ]), EntityTypes.rotation_quantity))

        numToGenerate -= 1


def main():
    train(getLoginCreds(), 'Kora', generateTrainingPhrases())

main()