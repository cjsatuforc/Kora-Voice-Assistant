from random import randint
import random

from witAutoTrainer import train, Entity, TrainingPhrase

class EntityTypes():
    rotation_quantity = 'rotation_quantity'
    units = 'units'
    direction = 'direction'

    # IMPORTANT: for wit builtin types like 'wit/number', just put whatever comes after 'wit/' e.g. 'number'
    #            Also, don't have any custom entities that collide with these e.g. don't have a custom 'number' entity
    wit_number = 'number'

class Intents():
    rotate = 'rotate'
    save = 'save'

def getLoginCreds():
    # Change this to match whatever you need to get your personal loginCreds
    loginCredentials = None
    with open('./cr3d5', 'r') as f:
        data = [_.strip() for _ in f.read().splitlines()]
        loginCredentials = {'username': data[0], 'password': data[1][1::2]}
    return loginCredentials

def generateTrainingPhrases():
    for phrase in RandomRotate(10):
        yield phrase
    yield TrainingPhrase(Intents.save, 'save')

###############################
##                           ##
##     Phrase Generators     ##
##                           ##
###############################

def RandomRotate(numToGenerate):
    while numToGenerate:
        magnitude = random.random() * randint(0, 360)
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