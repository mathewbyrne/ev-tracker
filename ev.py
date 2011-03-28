#!/usr/local/bin/python


import csv
import argparse
import hashlib
import json


class EvSet(object):
    
    STATS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
    
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
        return '%s - %s' % (self.name, self.evs)


class NoSuchSpecies(Exception):
    """Raised when a search for a pokemon species fails."""
    def __init__(self, species):
        super(NoSuchSpecies, self).__init__(self)
        self.species = species


class EvDict(object):
    
    def __init__(self, filename='ev.csv'):
        self.name = {}
        self.number = {}
        
        for row in csv.reader(open(filename, 'rb')):
            number = int(row[0])
            name = row[1]
            evs = dict(zip(EvSet.STATS, map(int, row[3:9])))  # array_combine
            species = Species(number, name, evs)
            
            self.name[species.name.lower()] = self.number[species.number] = species
    
    def get_species(self, identifier):
        try:
            return self.number[int(identifier)] if identifier.isdigit() else self.name[identifier]
        except KeyError:
            raise NoSuchSpecies(identifier)


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
    print _dict.get_species(args.species)


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
        print 'No match found for %s' % e.species
    
    _tracker.save()

