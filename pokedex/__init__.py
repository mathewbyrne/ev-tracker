'''
A module for retrieving data about Pokemon species.
'''

import os
import sqlite3
import difflib

from pokemon import Species, EvSet


__all__ = ['NoSuchSpecies', 'AmbiguousSpecies', 'fetch_by_id', 'fetch_by_name' 'search']


_DB_FILE = os.path.join(os.path.dirname(__file__), 'pokedex.db')
_connection = sqlite3.connect(_DB_FILE)
_connection.row_factory = sqlite3.Row


class _SpeciesCache(object):
    '''
    A very simple caching mechanism for database species records. There are
    kept in memory until requested again.
    '''
    def __init__(self):
        self._cache = {'id': {}, 'name': {}}
        self.names = None
    
    def contains(self, field, value):
        return (field in self._cache and value in self._cache[field])
    
    def get(self, field, value):
        return self._cache[field][value]
    
    def add(self, species):
        self._cache['id'][species.id] = species
        self._cache['name'][species.name.lower()] = species


_cache = _SpeciesCache()


class NoSuchSpecies(Exception):
    '''Raised when a search for a Pokemon species fails.'''
    def __init__(self, identifier):
        super(NoSuchSpecies, self).__init__()
        self.identifier = identifier


class AmbiguousSpecies(NoSuchSpecies):
    '''Raised when several matches are found for a Pokemon name search.'''
    def __init__(self, identifier, matches):
        super(AmbiguousSpecies, self).__init__(identifier)
        self.matches = [fetch_by_name(match) for match in matches]


def _name_list():
    if _cache.names is None:
        _cache.names = [row[0] for row in _connection.execute('SELECT name FROM pokemon')]
    return _cache.names


def _fetch(field, value, sql):
    
    # Attempt to retrieve species from the cache.
    if _cache.contains(field, value):
        return _cache.get(field, value)
    
    # On cache failure, query the database given the provided data.
    rows = _connection.execute(sql, (value,)).fetchall()
    if len(rows) == 0:
        raise NoSuchSpecies(value)
    row = rows[0]
    
    # Build the Species object from the returned data.
    evs = EvSet.from_dict({'HP': row['ev_hp'],
                           'Attack': row['ev_attack'],
                           'Defense': row['ev_defense'],
                           'Special Attack': row['ev_special_attack'],
                           'Special Defense': row['ev_special_defense'],
                           'Speed': row['ev_speed']})
    species = Species(id=row['id'], name=row['name'], evs=evs)
    
    _cache.add(species)
    
    return species


def fetch_by_id(id):
    '''
    Fetch a Species object from the pokedex by it's pokedex id. NoSuchSpecies 
    will be raised if no match was found.
    '''
    return _fetch('id', int(id),
                  '''SELECT p.id AS id, name, ev_hp, ev_attack, ev_defense,
                     ev_special_attack, ev_special_defense, ev_speed
                     FROM pokemon AS p
                     JOIN stats AS s ON p.id = s.pokemon_id
                     WHERE p.id = ?''')


def fetch_by_name(name):
    '''
    Fetch a Species object from the pokedex by it's name. The fetch is case 
    insensetive. NoSuchSpecies will be raised if no match was found.
    '''
    return _fetch('name', name.lower(),
                  '''SELECT p.id AS id, name, ev_hp, ev_attack, ev_defense,
                     ev_special_attack, ev_special_defense, ev_speed
                     FROM pokemon AS p
                     JOIN stats AS s ON p.id = s.pokemon_id
                     WHERE lower(name) = ?''')


def search(input):
    '''
    Search for a Pokemon species by a string input. The input can be a string
    or integer value corresponding to the name or number of a species. If the
    string is a name, the search will attempt to find close matches as well
    as an exact match.
    
    Will raise NoSuchSpecies if no match is found, or AmbiguousSpecies if 
    there are close matches, but nothing exact.
    '''
    # Direct number search
    if type(input) == int or input.isdigit():
        return fetch_by_id(input)
    else:
        try:
            return fetch_by_name(input)
        except NoSuchSpecies as e:
            # No exact match was found, try a fuzzy search.
            matches = difflib.get_close_matches(input, _name_list())
            if len(matches) == 0:
                raise e
            else:
                raise AmbiguousSpecies(input, matches)

