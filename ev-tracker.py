#!/usr/local/bin/python
# coding=utf-8


import os
import argparse
import json
from shutil import copyfile

from pokemon import Pokemon, EvSet
import pokedex


class Tracker(object):
    
    @classmethod
    def from_json(cls, filename):
        tracker = cls()
        tracker.filename = filename
        try:
            fp = open(filename, 'r')
            data = json.load(fp)
            for id, spec in data['pokemon'].items():
                spec['species'] = pokedex.fetch(id=spec['species'])
                spec['evs'] = EvSet(spec['evs'])
                spec['id'] = int(id)
                pokemon = Pokemon(**spec)
                tracker.track(pokemon)
                if 'active' in data and data['active'] == int(id):
                    tracker.active = pokemon
        except IOError:
            pass  # Ignore missing tracking file.
        
        return tracker
    
    @staticmethod
    def to_json(tracker, filename=None):
        filename = tracker.filename if filename is None else filename
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
        if id not in self.pokemon:
            raise NoTrackedPokemon(id)
        return self.pokemon[id]
    
    def unique_id(self):
        while self.counter in self.pokemon:
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


_tracker = None


def _save_tracker():
    if os.path.exists(_tracker.filename):
        copyfile(_tracker.filename,  _tracker.filename + '.bak')  # Create backup
    Tracker.to_json(_tracker)


def _cmd_ev(args):
    print pokedex.search(args.species)


def _cmd_list(args):
    print _tracker


def _cmd_track(args):
    species = pokedex.search(args.species)
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
    parser.add_argument('--infile', '-i', default=os.path.expanduser('~/.ev-tracker'))
    
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
        _tracker = Tracker.from_json(args.infile)
        args.func(args)
    except NoSuchSpecies as e:
        print 'No match found for \'%s\'.' % e.identifier
        if isinstance(e, AmbiguousSpecies):
            print 'Did you mean:'
            for match in e.matches:
                print '  %s' % pokedex.fetch(name=match)
    except NoActivePokemon:
        print 'No tracked Pokemon is marked as active.'
        print 'Set an active pokemon using the \'active --switch\' command.'
    except NoTrackedPokemon as e:
        print 'No tracked Pokemon with id \'%d\' was found.' % e.id

