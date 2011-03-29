# Pokémon EV Tracker

A small utility for keeping track of Effort Values while training Pokemon. 
Pokemon are added to the utility to be tracked

Usage:

	ev.py list
	> No tracked Pokemon
	
	ev.py track Magikarp --name=Ultrados --pokerus
	> 1 Ultrados (Magikarp)
	
	ev.py track 610
	> 2 Axew
	
	ev.py current
	> 2 Axew
	
	ev.py list
	>1 Ultrados (Magikarp)
	>2 Axew
	
	ev.py switch 1
	>1 Ultrados (Magikarp)
	
	ev.py status
	>1 Ultrados (Magikarp)
	>No EVs
	
	ev.py battle Lillipup
	>1 Ultrados - +2 Attack
	
	ev.py battle Lillipup -n3
	>1 Ultrados (Magikarp) - +6 Attack
	
	ev.py status
	>1 Ultrados (Magikarp)
	>Attack: 8
	
	ev.py update --item="Power Bracer"
	>1 Ultrados (Magikarp)
	
	ev.py battle 568
	>1 Ultrados (Magikarp) - +8 Attack, +2 Speed
	
	ev.py ev 600
	>Klang - +2 Defense
	
	ev.py -i
	>EV Tracker interactive mode
	>> 
	