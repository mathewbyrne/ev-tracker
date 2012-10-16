

ITEMS = {
    'Macho Brace': lambda evs: evs * 2,
    'Power Weight': lambda evs: evs + EvSet(hp=4),
    'Power Bracer': lambda evs: evs + EvSet(attack=4),
    'Power Belt': lambda evs: evs + EvSet(defense=4),
    'Power Lens': lambda evs: evs + EvSet(special_attack=4),
    'Power Band': lambda evs: evs + EvSet(special_defense=4),
    'Power Anklet': lambda evs: evs + EvSet(speed=4)
}


class EvSet(object):

    STATS = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
    LABELS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']

    MAX_STAT = 255
    MAX_EV = 510

    @staticmethod
    def label(stat):
        return EvSet.LABELS[EvSet.STATS.index(stat)]

    def __init__(self, hp=0, attack=0, defense=0, special_attack=0,
                 special_defense=0, speed=0):
        self.hp = int(hp)
        self.attack = int(attack)
        self.defense = int(defense)
        self.special_attack = int(special_attack)
        self.special_defense = int(special_defense)
        self.speed = int(speed)

    def __iadd__(self, other):
        for stat in EvSet.STATS:
            self.__dict__[stat] += other.__dict__[stat]
        return self

    def __add__(self, other):
        evs = self.clone()
        evs += other
        return evs

    def __imul__(self, integer):
        for stat in EvSet.STATS:
            self.__dict__[stat] *= integer
        return self

    def __mul__(self, integer):
        evs = self.clone()
        for stat in EvSet.STATS:
            evs.__dict__[stat] *= integer
        return evs

    def __str__(self):
        ev_string = ['+%d %s' % (ev, EvSet.label(stat)) for stat, ev in self.to_dict().items() if ev > 0]
        return ', '.join(ev_string)

    def verbose(self):
        ev_string = ['%s: %d' % (EvSet.label(stat), ev) for stat, ev in self.evs.items()]
        if not len(ev_string):
            return 'No EVs'
        return '\n'.join(ev_string)

    def clone(self):
        return EvSet(**self.to_dict())

    def to_dict(self):
        dict = {}
        for stat in EvSet.STATS:
            dict[stat] = self.__dict__[stat]
        return dict



class Species(object):

    def __init__(self, id, name, evs=None):
        self.id = int(id)
        self.name = name
        self.evs = EvSet() if evs is None else evs

    def __str__(self):
        return '#%03d %-10s %s' % (self.id, self.name, self.evs)


class Pokemon(object):

    @classmethod
    def from_dict(cls, dict):
        import pokedex
        dict['species'] = pokedex.fetch_by_id(dict['species'])
        dict['evs'] = EvSet(**dict['evs'])
        return cls(**dict)

    def __init__(self, id, species, name=None, item=None, pokerus=False, evs=None):
        self.id = int(id)
        self.species = species
        self._name = None
        self.name = name
        self.item = item
        self.pokerus = pokerus
        self.evs = EvSet() if evs is None else evs

    name = property(lambda self: self.get_name(),
                    lambda self, name: self.set_name(name))

    item = property(lambda self: self._item,
                    lambda self, item: self.set_item(item))

    def get_name(self):
        return self.species.name if self._name is None else self._name

    def set_name(self, name):
        if name is not None and len(name.strip()) > 0:
            self._name = name.strip()

    def set_item(self, item):
        if item is not None and item not in ITEMS:
            raise ValueError("Invalid item '%s'" % item)
        self._item = ITEMS[item] if item is not None else None

    def __str__(self):
        name = self.name
        if self._name is not None:
            name = '%s (%s)' % (name, self.species.name)
        if self.id is None:
            return name
        else:
            return '%d %s' % (self.id, name)

    def status(self):
        status = [str(self)]
        if self.pokerus:
            status.append('Pokerus')
        if self.item:
            status.append(self.item)
        status.append(self.evs.verbose())
        return '\n'.join(status)

    def listing(self, active):
        padding = '* ' if self is active else '  '
        return '%s%s' % (padding, self)

    def battle(species, number=1):
        '''
        Alter's a tracked Pokemons EVs to simulate having battled a Species.
        These values are altered by pokerus and any item held. The EV
        increment can be multiplied by number to simulate multiple battles.
        '''
        evs = species.evs.clone()
        if self.item is not None:
            evs = self.item(evs)
        if self.pokerus:
            evs *= 2
        self.evs += evs * number

    def to_dict(self):
        return {'species': self.species.id, 'name': self._name,
                'pokerus': self.pokerus, 'item': self.item,
                'evs': self.evs.to_dict(), 'id': self.id}

