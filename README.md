IKGen 0.0.2
=============

A command line character generator for the Iron Kingdoms RPG. 

Usage
---------------------------

    Usage: ikg (options)
           ikg serv (options)

    Character Generation Options:
        -r, --race STR       IK race, e.g., 'Human (Cygnaran)' or 'Nyss'.
        -a, --archetype STR  One of 'Gifted', 'Mighty', 'Skilled', or 'Intellectual'.
        -c, --careers STR    A JSON-formatted list of careers, e.g., '["Solder", "Thief"]'.
        -s, --stats STR      A JSON-formatted dict of attributes, e.g., '{"PER":8}'.
        -l, --list           List possible races, classes, and archetypes.
        -h --help
        --version

    Web Service Options:
        -n, --hostname HOST  The hostname of the web service. [default: localhost]
        -p, --port PORT      An open port to listen on. [default: 8080]

Example
-------
The following command will generate a Cygnaran Investigator/Arcanist (Illiminated) with a PER of 4. Note that specified attributes overwrite randomly generated ones, and may override race or career limits.

    ikg -r 'Human (Cygnaran)' -c '["Investigator", "Arcanist (Illuminated)"]' -a 'Gifted' -s '{"PER":4}'

Parameters can also be passed to the web service as an HTTP GET. Note that parameters with special characters should be urlencoded.

    http://localhost:8080/ikgen?race=Human%20\(Cygnaran\)&careers=["Investigator",%20"Arcanist%20(Illuminated)"]&archetype=Gifted&stats={"PER":4}

These parameters might return, for example, the following output:
    
    Name: Eliass Talley
    Race: Human (Cygnaran: Caspian)
    Gender: Male
    Measurements: 6'1", 144 lbs.
    Careers: Investigator, Arcanist (Illuminated)
    Archetype: Gifted
    Level: Hero
    Stats: PHY 6, SPD 6, STR 4
           AGL 4, PRW 4, POI 4
           INT 3, ARC 3, PER 4
           DEF 14, ARM 6, Init 14
           Cmd 3, Will 9
    Life: PHY 1-2 (-2 STR) ⬜ ⬜ ⬜ ⬜ ⬜ ⬜
          AGL 3-4 (-2 ATT) ⬜ ⬜ ⬜ ⬜
          INT 5-6 (-2 DEF) ⬜ ⬜ ⬜
    Benefits:
      Fast Caster: Gain one extra quick action each activation that can only be used to cast a spell.
      Rune Reader: Identify any spell cast in line of sight.  Learn the type of magic cast and tradition of caster.
      Hyper Perception: You gain boosted PER rolls.
    Abilities:
      Astute: The character can re-roll failed Detection rolls.
      Great Power: This character can upkeep one spell each turn without spending a Focus point or gaining a Fatigue point.
    Military Skills: Pistol 1
    Occupational Skills: Detection 1, Sneak 1, Research 1, Interrogation 1, Lore (Arcane) 1, Medicine 1, Law 1, Forensic Science 1
    Languages: Native (Cygnaran/Sulese, Khadoran, Llaelese, Ordic, Tribal) plus one more.
    Spells:                Cost  RNG  AOE POW  UP OFF
             Eyes of Truth    2 CTRL    –   – YES  NO
              Guided Blade    1    6    –   –  NO  NO
               Occultation    2    6    –   – YES  NO
    Connections: Order of Illumination
    GC: 175.0

Installation
------------
Standard Python package installation.

    > git clone http://github.org/gruevyhat/ikgen.git
    > cd ikgen
    > python setup.py install

Dependencies
------------
pandas >= 0.17.1  
numpy >= 1.10.2  
docopt >= 0.6.1  
bottle >= 0.12.8  

Acknowledgments
---------------
It would have been utterly impossible to put this together without the tabular data in Ski Anderson's very nice [Character Generator](http://privateerpressforums.com/showthread.php?158365-IKRPG-Generator-Tools).

Note that Iron Kingdoms and related content are exclusively trade marked by [Privateer Press](http://privateerpress.com/). The `ikgen` application is neither connected with nor endorsed by Privateer Press in any way, shape or form. 

Change History
--------------
0.0.1 - Initial version.  
0.0.2 - Added web service to CLI.
