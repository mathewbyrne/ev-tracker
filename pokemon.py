

class EvSet(object):
    
    STATS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
    
    MAX_STAT = 255
    MAX_EV = 510
    
    @classmethod
    def from_dict(cls, dict):
        evs = cls()
        for stat, ev in dict.items():
            if stat in EvSet.STATS and int(ev) > 0:
                evs.evs[stat] = int(ev)
        return evs
    
    def __init__(self, evs={}):
        self.evs = {}
    
    def __add__(self, other):
        evs = dict(self.evs)  # clone
        for stat, ev in other.evs:
            evs[stat] = ev[stat] + ev
        return EvSet(evs)
    
    def __str__(self):
        ev_string = ['+%d %s' % (ev, stat) for stat, ev in self.evs.items()]
        return ', '.join(ev_string)
    
    def verbose(self):
        ev_string = ['%s: %d' % (stat, ev) for stat, ev in self.evs.items()]
        if not len(ev_string):
            return 'No EVs'
        return '\n'.join(ev_string)
    
    def to_dict(self):
        return self.evs


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
        dict['evs'] = EvSet.from_dict(dict['evs'])
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
    
    def get_name(self):
        return self.species.name if self._name is None else self._name
    
    def set_name(self, name):
        if name is not None and len(name.strip()) > 0:
            self._name = name.strip()
    
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

    def to_dict(self):
        return {'species': self.species.id, 'name': self._name,
                'pokerus': self.pokerus, 'item': self.item,
                'evs': self.evs.to_dict(), 'id': self.id}

