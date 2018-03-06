import copy

class Entity():
    def __init__(self, data, entityType):
        self.subEntities = []
        self.text = ""
        self.entityType = entityType

        if isinstance(data, list):
            if not entityType is _DefaultEntityTypes._pseudo_composite:
                raise ValueError("If data type == list, then entityType must == _pseudo_composite")
            self.text = " ".join([entity.text for entity in data])
            self.subEntities = data
        else:
            if entityType is _DefaultEntityTypes._pseudo_composite:
                raise ValueError("If data type is not list, then entityType cannot be _pseudo_composite")
            if isinstance(data, int) or isinstance(data, float):
                data = str(data)

            if isinstance(data, str):
                self.text = data
            elif isinstance(data, Entity):
                if data.entityType == _DefaultEntityTypes._pseudo_composite:
                    self.text = data.text
                    self.subEntities = copy.deepcopy(data.subEntities)
                else:
                    self.text = data.text
                    self.subEntities = data

    def data(self):
        ret = {'text': self.text, 'type': self.entityType}
        entities = [entity.data() for entity in self.subEntities]
        if entities:
            ret['entities'] = entities

        return ret

    def __add__(self, other):
        if isinstance(other, int):
            other = str(other)

        if isinstance(other, str):
            return self + Entity(other, _DefaultEntityTypes._not_set)
        elif isinstance(other, Entity):
            if self.entityType == _DefaultEntityTypes._pseudo_composite:
                if other.entityType == _DefaultEntityTypes._pseudo_composite:
                    return Entity(_usefulEntities(copy.deepcopy(self.subEntities)) + _usefulEntities(copy.deepcopy(other.subEntities)), _DefaultEntityTypes._pseudo_composite)
                else:
                    return Entity(_usefulEntities(copy.deepcopy(self.subEntities)) + _usefulEntities([copy.deepcopy(other)]), _DefaultEntityTypes._pseudo_composite)
            else:
                if other.entityType == _DefaultEntityTypes._pseudo_composite:
                    return Entity(_usefulEntities([copy.deepcopy(self)]) + _usefulEntities(copy.deepcopy(other.subEntities)), _DefaultEntityTypes._pseudo_composite)
                else:
                    return Entity(_usefulEntities([copy.deepcopy(self), copy.deepcopy(other)]), _DefaultEntityTypes._pseudo_composite)

        raise NotImplementedError("Unsupported operator + in operation: E + " + str(type(other).__name__))

    def __radd__(self, other):
        if isinstance(other, int):
            other = str(other)

        if isinstance(other, str):
            return Entity(other, _DefaultEntityTypes._not_set) + self
        elif isinstance(other, Entity):
            if self.entityType == _DefaultEntityTypes._pseudo_composite:
                if other.entityType == _DefaultEntityTypes._pseudo_composite:
                    return Entity(copy.deepcopy(other.subEntities)+ copy.deepcopy(self.subEntities), _DefaultEntityTypes._pseudo_composite)
                else:
                    return Entity([copy.deepcopy(other)] + copy.deepcopy(self.subEntities), _DefaultEntityTypes._pseudo_composite)
            else:
                if other.entityType == _DefaultEntityTypes._pseudo_composite:
                    return Entity(copy.deepcopy(other.subEntities) + [copy.deepcopy(self)], _DefaultEntityTypes._pseudo_composite)
                else:
                    return Entity([copy.deepcopy(other), copy.deepcopy(self)], _DefaultEntityTypes._pseudo_composite)

        raise NotImplementedError("Unsupported operator + in operation: E + " + str(type(other).__name__))

    def __str__(self):
        return self.text

class _DefaultEntityTypes():
    # special entities not used in WIT, just for identification purposes
    _not_set = ''
    _pseudo_composite = '_psuedo_composite'

def _usefulEntities(entities):
    return [entity for entity in entities if entity.text]

class TrainingPhrase():
    def __init__(self, intent, phraseData):
        self._instructions = [{'entity': 'intent', 'value': intent}]
        self.currentInstruction = 0

        if isinstance(phraseData, str):
            self.text = phraseData
        elif isinstance(phraseData, Entity):
            self.text = phraseData.text
            entityData = phraseData.data()
            def createHighlightInstructions(data, textStartIndex):
                instructions = []
                if not data['type'] is _DefaultEntityTypes._pseudo_composite and not data['type'] is _DefaultEntityTypes._not_set:
                    instructions = [{'entity': data['type'], 'value': data['text'], 'startHighlight': textStartIndex, 'endHighlight': textStartIndex + len(data['text'])}]
                if 'entities' in data:
                    for e in data['entities']:
                        instructions += createHighlightInstructions(e, data['text'].index(e['text']) + textStartIndex)
                return instructions
            self._instructions += createHighlightInstructions(entityData, 0)
        else:
            raise NotImplementedError("Argument phraseData of TrainingPhrase constructor must be of type str or Entity, cannot be " + str(type(phraseData).__name__))

    def instructions(self):
        while self.currentInstruction < len(self._instructions):
            yield self._instructions[self.currentInstruction]
            self.currentInstruction += 1
