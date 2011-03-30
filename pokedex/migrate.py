

import csv
import sqlite3


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


CSV_FILE = 'ev.csv'
SQLITE_DB = 'pokedex.db'
STATS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']


POKEMON_TABLE_SQL = '''
CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT
)
'''
STATS_TABLE_SQL = '''
CREATE TABLE stats (
    id INTEGER PRIMARY KEY,
    pokemon_id INTEGER,
    ev_hp INTEGER,
    ev_attack INTEGER,
    ev_defense INTEGER,
    ev_special_attack INTEGER,
    ev_special_defense INTEGER,
    ev_speed INTEGER,
    form TEXT
)
'''
POKEMON_INSERT_SQL = '''INSERT INTO pokemon VALUES (?, ?)'''
STATS_INSERT_SQL = '''INSERT INTO stats VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)'''


if __name__ == '__main__':
    
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS pokemon')
    c.execute('DROP TABLE IF EXISTS stats')
    c.execute(POKEMON_TABLE_SQL)
    c.execute(STATS_TABLE_SQL)
    
    for row in unicode_csv_reader(open(CSV_FILE, 'rb')):
        form = None
        try:
            c.execute(POKEMON_INSERT_SQL, row[:2])
        except sqlite3.IntegrityError:
            print 'Alternate form:', row
            form = row[8]
        c.execute(STATS_INSERT_SQL, row[0:1] + row[2:8] + [form])
    
    conn.commit()
    c.close()

