# Pokémon EV Tracker

A small utility for keeping track of Effort Values while training Pokemon. 
Pokemon are added to the utility to be tracked

## Usage examples

To query the database for a Pokemon species and their EV yield, use the `ev`
command. This takes either the Pokedex number of a species or the species 
name. If the name is provided but not found, a fuzzy search is done to return
possible matches:
	
	ev.py ev 600
	>#600 Klang      +2 Defense
	
	ev.py ev Charizard
	>#006 Charizard  +3 Special Attack
	
	ev.py ev lia
	>No match found for 'lia'
	>Did you mean:
	>  #249 Lugia      +3 Special Defense
	>  #484 Palkia     +3 Special Attack
	>  #166 Ledian     +2 Special Defense

To see which Pokemon you are currently tracking use the `list` command:

	ev.py list
	> No tracked Pokemon

To track a new Pokemon use the `track` command. The integer value is the id
of the newly tracked Pokemon:

	ev.py track Magikarp --name=Ultrados --pokerus
	> 1 Ultrados (Magikarp)

You can also track a new Pokemon by it's Pokedex number.
	
	ev.py track 610
	> 2 Axew

The tracker always has an active Pokemon that other commands will operate on
by default. You can see the current Pokemon using the `current` command:
	
	ev.py list
	>1 Ultrados (Magikarp)
	>2 Axew
	
	ev.py current
	> 2 Axew

You can also switch the active Pokemon using the `current` command:

	ev.py current 1
	>1 Ultrados (Magikarp)

You can get the full status of the current Pokemon using the `status` command:

	ev.py status
	>1 Ultrados (Magikarp)
	>Pokerus
	>No EVs

To record battles and update EV values, use the `battle` command:

	ev.py battle Lillipup
	>Battled #506 Lillipup   +1 Attack
	>1 Ultrados - +2 Attack

You can also record multiple battles using the `-n` or `--number` option of 
the `battle` command:

	ev.py battle Lillipup -n3
	>Battled 3 × #506 Lillipup   +1 Attack
	>1 Ultrados (Magikarp) - +6 Attack
	
	ev.py status
	>1 Ultrados (Magikarp)
	>Pokerus
	>Attack: 8

To update the status of the current Pokemon, use the `update` command:
	
	ev.py update --item="Power Bracer"
	>1 Ultrados (Magikarp)

As with the other commands, you can refer to a Pokemon species by number:
	
	ev.py battle Trubish
	>No match found for 'Trubish'
	>Did you mean:
	>  #568 Trubbish   +1 Speed
	
	ev.py battle 568
	>Battled #568 Trubbish  +1 Speed
	>1 Ultrados (Magikarp) - +8 Attack, +2 Speed

## EV Calculations

I'm still fairly new to min/max Pokemon training, but my understanding of 

## Storage

Currently the tracker saves after every operation to a file your User 
directory called `.ev-tracker`. This will be a different location depending on 
your operating system. The file itself is in JSON format and therefore is 
fairly trivial to include in other projects.

## Issues, Contact etc.
`ev-tracker` was hacked together very quickly to provide a fairly minimal set
of functionality for my own personal needs. If you use this and have any 
issues then please let me know.

If you'd like to contribute or provide feedback, then 
[github](https://github.com/mathewbyrne/ev-tracker) is the best place to do 
that.
