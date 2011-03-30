'''
A module for retrieving data about Pokemon species.
'''

import os
import sqlite3
import difflib

from pokemon import Species, EvSet


__all__ = ['NoSuchSpecies', 'AmbiguousSpecies', 'fetch', 'search']


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
	
	def search(key, value):
		return self._cache[key][value]
	
	def add(species):
		self._cache['id'][species.id] = species
		self._cache['name'][species.name] = species


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
        self.matches = matches


_SELECT_SQL = '''SELECT p.id AS id, name, ev_hp, ev_attack, ev_defense,
                 ev_special_attack, ev_special_defense, ev_speed
                 FROM pokemon AS p
                 JOIN stats AS s ON p.id = s.pokemon_id
                 WHERE %s = ?'''


def _fetch(field, value):
    assert(field in ['id', 'name'])
    
    try:
        return _cache.search(field, value)
	except KeyError:
		pass
    
    rows = _connection.execute(SELECT_SQL % field, (value,)).fetchall()
    
    if len(rows) == 0:
        raise NoSuchSpecies(value)
    
    return rows


def _name_list():
    return [row[0] for row in _connection.execute('''SELECT name FROM pokemon''')]


def fetch(id=None, name=None):
    '''
    Fetch a Species object from the pokedex by either it's id or name. At 
    least one value must be provided or an will be raised. id takes
    precedence over name, and name will be ignored if it is specified.
    '''
    assert(id is not None or name is not None)
    
    rows = _fetch('id', id) if name is None else _fetch('name', name)
    row = rows[0]
    
    evs = EvSet({'HP': row['ev_hp'],
                 'Attack': row['ev_attack'],
                 'Defense': row['ev_defense'],
                 'Special Attack': row['ev_special_attack'],
                 'Special Defense': row['ev_special_defense'],
                 'Speed': row['ev_speed']})
    species = Species(id=row['id'], name=row['name'], evs=evs)
    
    _cache.add(species)
    
    return species


def search(input):
    '''
    Search for a Pokemon species by a string input. The input can be a string
    or integer value corresponding to the name or number of a species. If the
    string is a name, the search will attempt to find close matches as well
    as an exact match.
    
    Will raise NoSuchSpecies if no match is found, or AmbiguousSpecies if 
    there are close matches, but nothing exact.
    '''
    if input.isdigit():
        return fetch(id=int(input))
    else:
        try:
            return fetch(name=input.lower())
        except NoSuchSpecies as e:
            matches = difflib.get_close_matches(input, _name_list(), n=3)
            if len(matches) == 0:
                raise e
            else:
                raise AmbiguousSpecies(input, matches)

