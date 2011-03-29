#!/usr/local/bin/python


import os
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
    
    def __str__(self):
        ev_string = []
        for stat, ev in self.evs.items():
            ev_string.append('+%d %s' % (ev, stat))
        return ', '.join(ev_string)
    
    def json(self):
        return self.evs


class Species(object):
    
    def __init__(self, number, name, evs):
        self.number = int(number)
        self.name = name
        self.evs = evs if isinstance(evs, EvSet) else EvSet(evs)
    
    def __str__(self):
        return '#%03d %-10s %s' % (self.number, self.name, self.evs)


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
    
    @classmethod
    def from_csv(cls, filename):
        ev_dict = cls()
        for row in csv.reader(open(filename, 'rb')):
            number, name = row[:2]
            evs = dict(zip(EvSet.STATS, map(int, row[2:8])))  # array_combine
            ev_dict.add_species(Species(number, name, evs))
        return ev_dict
    
    def __init__(self):
        self._name = {}
        self._number = {}
    
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
                return self._number[int(identifier)]
            except KeyError:
                raise NoSuchSpecies(identifier)
        else:
            try:
                return self._name[identifier.lower()]
            except KeyError:
                matches = difflib.get_close_matches(identifier, self._name.keys(), n=3)
                if len(matches) == 0:
                    raise NoSuchSpecies(identifier)
                else:
                    raise AmbiguousSpecies(identifier, matches)


class Pokemon(object):
    
    def __init__(self, species, name=None, item=None, pokerus=False, evs=None):
        self.species = species
        self.name = name if name is not None else species.name
        self.item = item
        self.pokerus = pokerus
        self.evs = EvSet() if evs is None else evs
    
    def __str__(self):
        name = self.name
        if self.species.name != name:
            name = '%s (%s)' % (name, species.name)
        return name
    
    def json(self):
        return {'species': self.species.number, 'name': self.name,
                'pokerus': self.pokerus, 'item': self.item,
                'evs': self.evs.json()}


class Tracker(object):
    
    @classmethod
    def from_json(cls, filename, ev_dict):
        tracker = cls()
        
        try:
            fp = open(filename, 'r')
            data = json.load(fp)
            tracker.current = data['current']
            for id, pokemon in data['pokemon'].items():
                pokemon['species'] = ev_dict.number[pokemon['species']]
                pokemon['evs'] = EvSet(pokemon['evs'])
                tracker.track_pokemon(Pokemon(**pokemon))
        except IOError:
            pass  # Ignore missing tracking file.
        
        return tracker
    
    @staticmethod
    def to_json(tracker, filename):
        fp = open(filename, 'w')
        data = {'current': tracker.current, 'pokemon': {}}
        for id, pokemon in tracker.pokemon.items():
            data['pokemon'][id] = pokemon.json()
        json.dump(data, fp)
        fp.close()
    
    pokemon = {}
    
    def __init__(self):
        self.current = None
        self.counter = 0
    
    def track_pokemon(self, pokemon):
        self.counter += 1
        self.pokemon[self.counter] = pokemon
        if self.current is None:
            self.current = self.counter
        return '%d %s' % (self.counter, pokemon)
    
    def __str__(self):
        if len(self.pokemon):
            return '\n'.join(['%d %s' % (id, pokemon)
                              for id, pokemon in self.pokemon.items()])
        else:
            return 'No tracked Pokemon'


_ev_dict = EvDict.from_csv('ev.csv')
_tracker_filename = os.path.expanduser('~/.ev-tracker')
_tracker = Tracker.from_json(_tracker_filename, _ev_dict)


def _cmd_ev(args):
    print _ev_dict.search(args.species)


def _cmd_list(args):
    print _tracker


def _cmd_track(args):
    species = _ev_dict.search(args.species)
    pokemon = Pokemon(species=species, name=args.name)
    print _tracker.track_pokemon(pokemon)
    Tracker.to_json(_tracker, _tracker_filename)


def _cmd_remove(args):
    pokemon = _tracker.find(args.id)


def _build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    ev_parser = subparsers.add_parser('ev', help='List Effort Values for a Pokemon')
    ev_parser.add_argument('species', help='Name or number of Pokemon Species to search for')
    ev_parser.set_defaults(func=_cmd_ev)
    
    list_parser = subparsers.add_parser('list', help='List tracked Pokemon')
    list_parser.set_defaults(func=_cmd_list)
    
    track_parser = subparsers.add_parser('track', help='Add a Pokemon to track')
    track_parser.add_argument('species')
    track_parser.add_argument('--name')
    track_parser.set_defaults(func=_cmd_track)
    
    remove_parser = subparsers.add_parser('remove', help='Stop tracking a Pokemon')
    remove_parser.add_argument('id')
    remove_parser.set_defaults(func=_cmd_remove)
    
    return parser


if __name__ == '__main__':
    try:
        args = _build_parser().parse_args()
        args.func(args)
    except NoSuchSpecies as e:
        print 'No match found for \'%s\'' % e.identifier
        if isinstance(e, AmbiguousSpecies):
            print 'Did you mean:'
            for match in e.matches:
                print '  %s' % _ev_dict.name[match]

