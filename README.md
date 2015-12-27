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

Change History
--------------
0.0.1 - Initial version.  
0.0.2 - Added web service to CLI.
