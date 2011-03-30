'''
A module for retrieving data about Pokemon species.
'''

import os
import sqlite3
import difflib

from .pokemon import Species, EvSet


__all__ = ['NoSuchSpecies', 'AmbiguousSpecies', 'fetch', 'search']


_DB_FILE = os.path.join(os.path.dirname(__file__), 'pokedex.db')
_connection = sqlite3.connect(_DB_FILE)
_connection.row_factory = sqlite3.Row


_id_cache = {}
_name_cache = {}


def _cache(species):
    _id_cache[species.id] = species
    _name_cache[species.name] = species


def _get_names():
    return [row[0] for row in _connection.execute('''SELECT name FROM pokemon''')]


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


_SELECT_SQL = '''SELECT p.id AS id, name, ev_hp, ev_attack, ev_defense,
                 ev_special_attack, ev_special_defense, ev_speed
                 FROM pokemon AS p
                 JOIN stats AS s ON p.id = s.pokemon_id'''


def fetch(id=None, name=None):
    '''
    Fetch a Species object from the pokedex by either it's id or name. At 
    least one value must be provided or an will be raised. id takes
    precedence over name, and name will be ignored if it is specified.
    '''
    assert(id is not None or name is not None)
    
    if id is not None:
        if id in _id_cache:
            return _id_cache[id]
        rows = _connection.execute('%s %s' % (_SELECT_SQL, 'WHERE p.id = ?'),
                                   (id,)).fetchall()
        row = rows[0]
    
    elif name is not None:
        if name in _name_cache:
            return _name_cache[name]
        rows = _connection.execute('%s %s' % (_SELECT_SQL, 'WHERE p.name = ?'),
                                   (name,)).fetchall()
        row = rows[0]
    
    evs = EvSet({'HP': row['ev_hp'],
                 'Attack': row['ev_attack'],
                 'Defense': row['ev_defense'],
                 'Special Attack': row['ev_special_attack'],
                 'Special Defense': row['ev_special_defense'],
                 'Speed': row['ev_speed']})
    species = Species(id=row['id'], name=row['name'], evs=evs)
    
    _cache(species)
    
    return species


def search(input):
    '''
    Search for a Pokemon species by a string input. The input can be a string
    or integer value corresponding to the name or number of a species. If the
    string is a name, the search will attempt to find close matches as well
    as an exact match.
    '''
    if input.isdigit():
        try:
            return fetch(id=int(input))
        except KeyError:
            raise NoSuchSpecies(input)
    else:
        try:
            return fetch(name=input.lower())
        except KeyError:
            matches = difflib.get_close_matches(input, _get_names(), n=3)
            if len(matches) == 0:
                raise NoSuchSpecies(input)
            else:
                raise AmbiguousSpecies(input, matches)

