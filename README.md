# Pokémon EV Tracker

Usage:

	ev.py list
	> f0 Ultrados
	
	ev.py add Magikarp --name=Ultrados --pokerus
	> f0 Ultrados
	
	ev.py release f0
	> f0 Ultrados
	
	ev.py add 610
	> 3a Axew
	
	ev.py current
	> 3a Axew
	
	ev.py list
	>3a Axew
	>f0 Ultrados
	
	ev.py switch f0
	>f0 Ultrados
	
	ev.py status
	>f0 Ultrados - Magikarp
	>No EVs
	
	ev.py battle Lillipup
	>f0 Ultrados - +2 Attack
	
	ev.py status
	>f0 Ultrados - Magikarp
	>Attack: 2
	
	ev.py update f0 --item="Power Bracer"
	>f0 Ultrados
	
	ev.py battle 568
	>f0 Ultrados - +4 Attack, +2 Speed
	
	ev.py ev 600
	>Klang - +2 Defense
	