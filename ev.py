#!/usr/local/bin/python
# coding=utf-8


import os
import csv
import argparse
import json
import difflib
from shutil import copyfile


class EvSet(object):
    
    STATS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
    
    MAX_STAT = 255
    MAX_EV = 510
    
    def __init__(self, evs={}):
        self.evs = {}
        for stat, ev in evs.items():
            if stat in EvSet.STATS and int(ev) > 0:
                self.evs[stat] = int(ev)
    
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
    
    def __init__(self, species, name=None, item=None, pokerus=False, evs=None, id=None):
        self.id = id
        self.species = species
        self.name = name if name is not None else species.name
        self.item = item
        self.pokerus = pokerus
        self.evs = EvSet() if evs is None else evs
    
    def __str__(self):
        name = self.name
        if self.species.name != name:
            name = '%s (%s)' % (name, species.name)
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
            for id, spec in data['pokemon'].items():
                spec['species'] = ev_dict.number[spec['species']]
                spec['evs'] = EvSet(spec['evs'])
                spec['id'] = int(id)
                pokemon = Pokemon(**spec)
                tracker.track(pokemon)
                if 'active' in data.keys() and data['active'] == int(id):
                    tracker.active = pokemon
        except IOError:
            pass  # Ignore missing tracking file.
        
        return tracker
    
    @staticmethod
    def to_json(tracker, filename):
        fp = open(filename, 'w')
        data = {'pokemon': {}}
        try:
            data['active'] = tracker.active.id
        except NoActivePokemon:
            pass
        for id, pokemon in tracker.pokemon.items():
            data['pokemon'][id] = pokemon.json()
        json.dump(data, fp)
        fp.close()
    
    pokemon = {}
    
    def __init__(self):
        self._active = None
        self.counter = 1
    
    active = property(lambda self: self.get_active(),
                      lambda self, pokemon: self.set_active(pokemon))
    
    def get_active(self):
        if self._active is None:
            raise NoActivePokemon()
        return self._active
    
    def set_active(self, pokemon):
        self._active = pokemon
    
    def get_pokemon(self, id):
        if id not in self.pokemon.keys():
            raise NoTrackedPokemon(id)
        return self.pokemon[id]
    
    def unique_id(self):
        while self.counter in self.pokemon.keys():
            self.counter += 1
        return self.counter
    
    def track(self, pokemon):
        if pokemon.id is None:
            pokemon.id = self.unique_id()
        self.pokemon[pokemon.id] = pokemon
        if self._active is None:
            self._active = pokemon
    
    def untrack(self, pokemon):
        del self.pokemon[pokemon.id]
        pokemon.id = None
        if self._active is pokemon:
            self._active = None
    
    def __str__(self):
        if len(self.pokemon):
            return '\n'.join([pokemon.listing(self._active) for pokemon in self.pokemon.values()])
        else:
            return 'No tracked Pokemon'


class NoActivePokemon(Exception):
    """
    Raised when an operation that assumes the existence of an active Pokemon
    is carried out.
    """
    pass

class NoTrackedPokemon(Exception):
    """
    Raised when an id is requested from a Tracker but the Tracker does not
    have a Pokemon with the provided id.
    """
    def __init__(self, id):
        super(NoTrackedPokemon, self).__init__()
        self.id = id


_ev_dict = EvDict.from_csv('ev.csv')
_tracker_filename = os.path.expanduser('~/.ev-tracker')
_tracker = Tracker.from_json(_tracker_filename, _ev_dict)


def _save_tracker():
    copyfile(_tracker_filename, _tracker_filename + '.bak')  # Create backup
    Tracker.to_json(_tracker, _tracker_filename)


def _cmd_ev(args):
    print _ev_dict.search(args.species)


def _cmd_list(args):
    print _tracker


def _cmd_track(args):
    species = _ev_dict.search(args.species)
    pokemon = Pokemon(species=species, name=args.name, item=args.item,
                      pokerus=args.pokerus)
    _tracker.track(pokemon)
    print pokemon
    _save_tracker()


def _cmd_active(args):
    if args.switch:
        _tracker.active = _tracker.get_pokemon(args.switch)
        _save_tracker()
    print _tracker.active


def _cmd_status(args):
    if args.id is None:
        pokemon = _tracker.active
    else:
        pokemon = _tracker.get_pokemon(args.id)
    print pokemon.status()


def _cmd_remove(args):
    pokemon = _tracker.get_pokemon(args.id)
    _tracker.untrack(pokemon)
    print 'No longer tracking %s' % pokemon
    _save_tracker()


def _build_parser():
    parser = argparse.ArgumentParser(prog='ev', description='A small utility for keeping track of Effort Values while training Pokemon.')
    subparsers = parser.add_subparsers()
    
    ev_parser = subparsers.add_parser('ev', help='List Effort Values for a Pokemon')
    ev_parser.add_argument('species', help='Name or number of Pokemon species to search for')
    ev_parser.set_defaults(func=_cmd_ev)
    
    list_parser = subparsers.add_parser('list', help='List tracked Pokemon')
    list_parser.set_defaults(func=_cmd_list)
    
    track_parser = subparsers.add_parser('track', help='Add a Pokemon to track')
    track_parser.add_argument('species', help='Name of number of Pokemon species to track')
    track_parser.add_argument('--name', '-n', help='Nickname of Pokemon')
    track_parser.add_argument('--pokerus', '-p', action='store_true', default=False, help='Indicates the given Pokemon has Pokerus')
    track_parser.add_argument('--item', '-i')
    track_parser.set_defaults(func=_cmd_track)
    
    active_parser = subparsers.add_parser('active', help='List the active Pokemon')
    active_parser.add_argument('--switch', '-s', type=int, help='Switch the active Pokemon')
    active_parser.set_defaults(func=_cmd_active)
    
    status_parser = subparsers.add_parser('status', help='Show the status of the active Pokemon')
    status_parser.add_argument('--id', '-i', type=int)
    status_parser.set_defaults(func=_cmd_status)
    
    release_parser = subparsers.add_parser('release', help='Stop tracking a Pokemon')
    release_parser.add_argument('id', type=int)
    release_parser.set_defaults(func=_cmd_remove)
    
    return parser


if __name__ == '__main__':
    try:
        args = _build_parser().parse_args()
        args.func(args)
    except NoSuchSpecies as e:
        print 'No match found for \'%s\'.' % e.identifier
        if isinstance(e, AmbiguousSpecies):
            print 'Did you mean:'
            for match in e.matches:
                print '  %s' % _ev_dict.name[match]
    except NoActivePokemon:
        print 'No tracked Pokemon is marked as active.'
        print 'Set an active pokemon using the \'active --switch\' command.'
    except NoTrackedPokemon as e:
        print 'No tracked Pokemon with id \'%d\' was found.' % e.id

