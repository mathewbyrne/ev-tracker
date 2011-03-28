#!/usr/local/bin/python


import csv
import argparse


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


class Pokemon(object):
    
    def __init__(self, number, name, evs):
        self.number = int(number)
        self.name = name
        self.evs = evs if isinstance(evs, EvSet) else EvSet(evs)
    
    def __repr__(self):
        return '%s - %s' % (self.name, self.evs)


class PokemonDict(object):
    
    def __init__(self, filename='ev.csv'):
        self.name = {}
        self.number = {}
        
        for row in csv.reader(open(filename, 'rb')):
            number = int(row[0])
            name = row[1]
            evs = dict(zip(EvSet.STATS, map(int, row[3:9])))  # array_combine
            pokemon = Pokemon(number, name, evs)
            
            self.name[pokemon.name.lower()] = self.number[pokemon.number] = pokemon
    
    def get_pokemon(self, identifier):
        return self.number[int(identifier)] if identifier.isdigit() else self.name[identifier]


_dict = PokemonDict()
            

def _cmd_ev(args):
    try:
        print _dict.get_pokemon(args.pokemon)
    except KeyError:
        print 'No match found for %s' % args.pokemon
    

def _build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    ev_parser = subparsers.add_parser('ev', help='List Effort Values for a Pokemon')
    ev_parser.add_argument('pokemon', help='Name or number of Pokemon to search for')
    ev_parser.set_defaults(func=_cmd_ev)
    
    add_parser = subparsers.add_parser('add', help='Add a Pokemon to track')
    add_parser.add_argument('pokemon')
    add_parser.add_argument('name')
    
    return parser


if __name__ == '__main__':
    args = _build_parser().parse_args()
    args.func(args)
    
    #db = Database()
    #for pokemon in db.pokemon:
    #    print pokemon

