#!/usr/local/bin/python


import csv
import argparse
import hashlib
import json
import difflib


class EvSet(object):
    
    STATS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
    
    MAX_STAT = 255
    MAX_EV = 510
    
    def __init__(self, evs={}):
        self.evs = {}
        for stat, ev in evs.items():
            if stat in EvSet.STATS and int(ev) > 0:
                self.evs[stat] = int(ev)
    
    def __repr__(self):
        ev_string = []
        for stat, ev in self.evs.items():
            ev_string.append('+%d %s' % (ev, stat))
        return ', '.join(ev_string)


class Species(object):
    
    def __init__(self, number, name, evs):
        self.number = int(number)
        self.name = name
        self.evs = evs if isinstance(evs, EvSet) else EvSet(evs)
    
    def __repr__(self):
        return '#%03d %s - %s' % (self.number, self.name, self.evs)


class NoSuchSpecies(Exception):
    """Raised when a search for a Pokemon species fails."""
    def __init__(self, identifier):
        super(NoSuchSpecies, self).__init__()
        self.identifier = identifier


class AmbiguousSpecies(NoSuchSpecies):
    """Raised when several matches are found for a Pokemon name search."""
    def __init__(self, identifier, matches):
        super(AmbiguousSpecies, self).__init__(identifier)
        self.matches = matches


class EvDict(object):
    
    def __init__(self, filename='ev.csv'):
        self._name = {}
        self._number = {}
        for row in csv.reader(open(filename, 'rb')):
            number, name = row[:2]
            evs = dict(zip(EvSet.STATS, map(int, row[2:8])))  # array_combine
            self.add_species(Species(number, name, evs))
    
    def add_species(self, species):
        self._name[species.name.lower()] = species
        self._number[species.number] = species
    
    name = property(lambda self: self._name, doc="A mapping of Species names.")
    number = property(lambda self: self._number, doc="A mapping of Species numbers.")
    
    def search(self, identifier):
        """
        Search for a Pokemon species by a string identifier. The identifier
        can be a string or integer value corresponding to the name or number 
        of a species. If the string is a name, the search will attempt to find
        close matches as well as an exact match.
        """
        if identifier.isdigit():
            try:
                return self.number[int(identifier)]
            except KeyError:
                raise NoSuchSpecies(identifier)
        else:
            try:
                return self.name[identifier]
            except KeyError:
                matches = difflib.get_close_matches(identifier, self.name.keys(), n=3)
                if len(matches) == 0:
                    raise NoSuchSpecies(identifier)
                else:
                    raise AmbiguousSpecies(identifier, matches)


_dict = EvDict()


class Pokemon(object):
    
    _counter = 0
    
    def __init__(self, species, name=None, item=None, pokerus=False):
        self.species = species
        self.name = name if name is not None else species.name
        self.id = hashlib.sha1('%s%d' % (self.name, Pokemon._counter)).hexdigest()
        self.item = item
        self.pokerus = pokerus
    
    def __repr__(self):
        return '%s %s' % (self.id, self.name)


class Tracker(object):
    
    def __init__(self, filename):
        self.filename = filename
        
        try:
            fp = open(filename, 'r')
        except IOError:
            pass
    
    def add_pokemon(self, pokemon):
        pass
    
    def save(self):
        fp = open(self.filename, 'w')
        json.dump({}, fp)
        fp.close()


_tracker = Tracker(filename='tracker.json')
            

def _cmd_ev(args):
    print _dict.search(args.species)


def _cmd_add(args):
    species = _dict.get_species(args.species)
    pokemon = Pokemon(species=species, name=args.name)
    print pokemon


def _build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    ev_parser = subparsers.add_parser('ev', help='List Effort Values for a Pokemon')
    ev_parser.add_argument('species', help='Name or number of Pokemon Species to search for')
    ev_parser.set_defaults(func=_cmd_ev)
    
    add_parser = subparsers.add_parser('add', help='Add a Pokemon to track')
    add_parser.add_argument('species')
    add_parser.add_argument('--name')
    add_parser.set_defaults(func=_cmd_add)
    
    return parser


if __name__ == '__main__':
    try:
        args = _build_parser().parse_args()
        args.func(args)
    except NoSuchSpecies as e:
        print 'No match found for %s' % e.identifier
        if isinstance(e, AmbiguousSpecies):
            print 'Did you mean:'
            for match in e.matches:
                print _dict.name[match]
    
    _tracker.save()

