#!/usr/bin/env python


"""
Primary class for IKRPG character generation.

author: GVH
version: 0.0.1
"""

# TODO: Apply experience.
# TODO: Write FDF output for PDF generation.

import os
import re
import pandas as pd
import numpy as np
from random import choice
from collections import defaultdict
from fdfgen import forge_fdf


SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)) 

SKILL = re.compile("(?!<: )([A-Z][^,:]+?) ([0-9])")
CHOOSE_N = re.compile("Choose (?:one|two|three): (.*)")
KHARD_SFX = re.compile("([^aeiou])$")
MEAS = re.compile("(\d+)-(\d+) (?:in|lb)")

ARCHETYPES = [u'Gifted', u'Intellectual', u'Mighty', u'Skilled']
STATS = [u'PHY', u'SPD', u'STR', u'AGL', u'PRW', u'POI', u'INT', u'ARC', u'PER']
LEVELS = ['Hero', 'Veteran', 'Epic']


def sumdict(list_of_dicts):
    c = defaultdict(int)
    for d in list_of_dicts:
        for k, v in d.iteritems():
            c[k] += v
    return c


def parse(skills):
    S = []
    D = defaultdict(int)
    if skills.find("one:") > -1:
        S.append(choice(SKILL.findall(CHOOSE_N.findall(skills)[0])))
    if skills.find("two:") > -1:
        S.append(choice(SKILL.findall(CHOOSE_N.findall(skills)[0])))
        S.append(choice(SKILL.findall(CHOOSE_N.findall(skills)[0])))
    if skills.find("three:") > -1:
        S.append(choice(SKILL.findall(CHOOSE_N.findall(skills)[0])))
        S.append(choice(SKILL.findall(CHOOSE_N.findall(skills)[0])))
        S.append(choice(SKILL.findall(CHOOSE_N.findall(skills)[0])))
    S.extend(SKILL.findall(skills.split("Choose")[0]))
    for s, v in S:
        D[s] += int(v)
    return D


def choice_geom(S, p=0.3):
    n = len(S)
    while n >= len(S):
        n = np.random.geometric(p) - 1
    return S[n]


def rand_meas(text):
    male, female = [(int(x), int(y)) for x, y in MEAS.findall(text)]
    return {'Male': choice(range(*male)), 'Female': choice(range(*female))} 


def title_caps(text):
    return ''.join([c.upper() if i == 0 else c.lower()
                    for i, c in enumerate(list(text))])


class CharData(object):
    careers = pd.read_csv(os.path.join(SCRIPTDIR, "data", "careers.csv"), encoding="utf8")
    races = pd.read_csv(os.path.join(SCRIPTDIR, "data", "races.csv"), encoding="utf8")
    stats = pd.read_csv(os.path.join(SCRIPTDIR, "data", "stats.csv"), encoding="utf8")
    connections = pd.read_csv(os.path.join(SCRIPTDIR, "data", "connections.csv"), encoding="utf8")
    abilities = pd.read_csv(os.path.join(SCRIPTDIR, "data", "abilities.csv"), encoding="utf8")
    archetypes = pd.read_csv(os.path.join(SCRIPTDIR, "data", "archetypes.csv"), encoding="utf8")
    benefits = pd.read_csv(os.path.join(SCRIPTDIR, "data", "benefits.csv"), encoding="utf8")
    spell_lists = pd.read_csv(os.path.join(SCRIPTDIR, "data", "spell_lists.csv"), encoding="utf8")
    spells = pd.read_csv(os.path.join(SCRIPTDIR, "data", "spells.csv"), encoding="utf8")
    weapons = pd.read_csv(os.path.join(SCRIPTDIR, "data", "weapons.csv"), encoding="utf8")
    armor = pd.read_csv(os.path.join(SCRIPTDIR, "data", "armor.csv"), encoding="utf8")
    xp = pd.read_csv(os.path.join(SCRIPTDIR, "data", "experience.csv"), encoding="utf8")
    names = pd.read_csv(os.path.join(SCRIPTDIR, "data", "names.csv"), encoding="utf8")


class LC(object):
    """Generates a random name from a Markov model of character
    probabilities."""
    def __init__(self, data=None, min_len=5, max_len=15):
        self.min_len = min_len
        self.max_len = max_len
        if data:
            self.fit(data)

    def fit(self, data):
        self.m = defaultdict(list)
        for w in data:
            w = " " + w + "_"
            if len(w) > 3:
                for c in range(len(w)-2):
                    self.m[w[c:c+2]].append(w[c+2])

    def generate(self):
        name = choice([w for w in self.m.keys()
                       if w.startswith(" ")])
        while name[-1] != "_":
            name += choice(self.m[name[-2:]])
        name = name.replace("_", "").strip()
        if not (self.min_len < len(name) < self.max_len):
            return self.generate()
        else:
            return name


class Character(object):

    def __init__(self, race=None, stats={},
                 archetype=None, benefits=[],
                 careers=[], spells=[], abilities=[],
                 connections=[], money=0,
                 assets=[], chardata=None):
        self.race = race
        self.archetype = archetype
        self.benefits = benefits
        self.fixed_stats = stats
        self.careers = careers
        self.spells = spells
        self.money = money
        self.assets = assets
        self.connections = connections
        self.abilities = abilities
        self.level = 'Hero'
        self.data = chardata or CharData()
        self.build()

    def summary(self):
        stats = ["Name: " + self.name]
        if self.subrace != '-':
            stats += ["Race: " + self.race.replace(")", ": " + self.subrace + ")")]
        else:
            stats += ["Race: " + self.race]
        stats += ["Gender: " + self.gender]
        stats += ["Measurements: %s\'%s\", %s lbs." % (self.height/12, self.height%12, self.weight)]
        stats += ["Careers: " + ", ".join(self.careers)]
        stats += ["Archetype: " + self.archetype]
        stats += ['Level: ' + self.level]
        stats += ["Stats: PHY %(PHY)d, SPD %(SPD)d, STR %(STR)d" % self.stats]
        stats += ["       AGL %(AGL)d, PRW %(PRW)d, POI %(POI)d" % self.stats]
        stats += ["       INT %(INT)d, ARC %(ARC)d, PER %(PER)d" % self.stats]
        stats += ["       DEF %(DEF)d, ARM %(ARM)d, Init %(Initiative)d, Cmd %(Command)d" % self.stats]
        stats += ["Life: PHY 1-2 (-2 STR) " + (u"\u2b1c " * self.stats['PHY'])]
        stats += ["      AGL 3-4 (-2 ATT) " + (u"\u2b1c " * self.stats['AGL'])]
        stats += ["      INT 5-6 (-2 DEF) " + (u"\u2b1c " * self.stats['INT'])]
        stats += ["Benefits:"]
        stats += ["  %s: %s" % (r['Benefit'], r['Description'])
                  for i, r in self.benefit_table.iterrows()]
        stats += ["Abilities:"]
        stats += ["  %s: %s" % (r['Ability'], r['Short Description'])
                  for i, r in self.ability_table.iterrows()]
        stats += ["Military Skills: " + ', '.join("%s %d" % i for i in self.skills_mil.items())]
        stats += ["Occupational Skills: " + ', '.join("%s %d" % i for i in self.skills_occ.items())]
        stats += ['Languages: ' + self.languages]
        if self.spells:
            stats += ["Spells:                Cost  RNG  AOE POW  UP OFF"]
            stats += ["  %20.20s %4.4s %4.4s %4.4s %3.3s %3.3s %3.3s" % tuple(r[0:7])
                      for i, r in self.spell_table.iterrows()]
        if self.connections:
            stats += ["Connections: " + ", ".join(self.connections)]
        if self.assets:
            stats += ["Assets: " + ", ".join(self.assets)]
        stats += ["GC: " + str(self.money)]
        return "\n".join(stats)

    def build(self):
        self._gen_race()
        self._gen_archetype()
        self._gen_benefits()
        self._gen_stats()
        self._gen_careers()
        self._gen_abilities()
        self._gen_skills()
        self._gen_spells()
        self._gen_connections()
        self._gen_money()
        self._gen_assets()
        self._gen_personal()
        self._gen_derived_stats()
        self._adjust_race()

    def _gen_race(self):
        if not self.race:
            self.race = choice_geom(self.data.races.Race)
        self.race_table = self.data.races[self.data.races.Race == self.race]

    def _gen_archetype(self):
        if not self.archetype:
            avail = [a for a in ARCHETYPES if (self.race_table[a] == 1).bool()]
            self.archetype_table = self.data \
                    .archetypes[self.data.archetypes.Archetype.isin(avail)].sample()
            self.archetype = self.archetype_table.Archetype.iat[0]
        else:
            self.archetype_table = self.data \
                .archetypes[self.data.archetypes.Archetype == self.archetype]

    def _gen_benefits(self):
        if not self.benefits:
            self.benefit_table = self.data \
                .benefits[self.data.benefits.Archetype == self.archetype].sample()
        else:
            self.benefit_table = self.data \
                .benefits[self.data.benefits.Benefit.isin(self.benefits)]
        self.benefits = self.benefit_table.Benefit.tolist()

    def _gen_careers(self):
        if self.careers:
            self.career_table = self.data \
                .careers[self.data.careers.Career.isin(self.careers)]
        else:
            # Limit by race
            mask = self.data.careers[self.race] == 1
            # Limit for archetype
            if self.archetype != "Gifted":
                mask &= self.data.careers.Gifted == 0
            if self.archetype != "Mighty":
                mask &= self.data.careers.Mighty == 0
            # Choose first career
            c1 = self.data.careers[mask].sample()
            # Limit by first career
            basename = c1.Career.tolist()[0].split()[0]
            mask &= self.data.careers.Career \
                .apply(lambda x: not x.startswith(basename))
            # Limit by first career restrictions
            c1_restr = [c for c in c1['Career Restrictions'].any().split(', ')
                        if c != '-']
            if c1_restr:
                mask &= self.data.careers.Career.isin(c1_restr)
            # Limit by second career restrictions
            mask &= self.data.careers['Career Restrictions'] \
                .apply(lambda x: x == '-' and x.find(basename) == -1)
            # Choose second career
            c2 = self.data.careers[mask].sample()
            self.career_table = pd.concat([c1, c2])
            self.careers = self.career_table.Career.tolist()
        # Handle bonus benefits
        self.benefits += [b for b in self.career_table['Benefit Bonus'].tolist()
                          if b != '-']
        self.benefit_table = self.data \
            .benefits[self.data.benefits.Benefit.isin(self.benefits)]
        # Handle bonus stats
        bonus_stats = sumdict(self.career_table['Bonus Stats'].apply(parse))
        self.stats = sumdict([self.stats, bonus_stats])
        for k, v in bonus_stats.items():
            for i in range(len(self.stat_table)):
                self.stat_table[k].iat[i] += v

    def _gen_abilities(self):
        if not self.abilities:
            self.abilities = self.career_table['Starting Abilities'] \
                .apply(lambda x: x.split(', ')) \
                .sum()
            self.ability_table = self.data \
                .abilities[self.data.abilities.Ability.isin(self.abilities)]

    def _gen_skills(self):
        self.skills_mil = sumdict(self.career_table['Starting Mil']
                                  .apply(parse).tolist())
        self.skills_occ = sumdict(self.career_table['Starting Occ']
                                  .apply(parse).tolist())

    def _gen_stats(self):
        self.stat_table = self.data.stats[self.data.stats.Race == self.race.split()[0]]
        self.stats = self.stat_table[STATS][self.stat_table.Set == 'Base'] \
            .iloc[0].to_dict()
        if self.archetype == "Gifted":
            self.stats['ARC'] = 2
        stat_sum = sum(self.stats.values())
        while sum(self.stats.values()) < stat_sum + 3:
            stat = choice_geom(self.archetype_table['Stat Order'].any().split(", "),
                               float(self.archetype_table['p']))
            limit = self.stat_table[self.stat_table.Set == self.level][stat] \
                .iloc[0]
            if self.stats[stat] < limit:
                self.stats[stat] += 1
        if self.fixed_stats:
            self.stats.update(self.fixed_stats)

    def _gen_derived_stats(self):
        self.stats[u'DEF'] = sum(self.stats[s] for s in ['AGL', 'SPD', 'PER'])
        self.stats[u'ARM'] = self.stats['PHY']
        self.stats[u'Initiative'] = sum(self.stats[s] for s in ['PRW', 'SPD', 'PER'])
        self.stats[u'Command'] = self.stats['INT']
        if 'Command' in self.skills_occ.keys():
            self.stats[u'Command'] += int(self.skills_occ['Command'])

    def _gen_spells(self):
        if self.archetype == "Gifted":
            spells = ', '.join(self.career_table['Starting Sp']).split(', ')
            self.spell_table = self.data \
                .spells[self.data.spells.Spell.isin(spells)]
            self.spells = set(self.spells + self.spell_table.Spell.tolist())

    def _gen_connections(self):
        conns = [c for c in
                 self.career_table['Starting Conns'].tolist()
                 if c != 'None']
        if conns:
            self.connections = set(self.connections + conns)

    def _gen_assets(self):
        assets = [a for a in
                  self.career_table.Assets.tolist()
                  if a != "-"]
        if assets:
            self.assets = set(self.assets + assets)

    def _gen_money(self):
        money = self.career_table.GC.sum()
        if money:
            self.money += money

    def _gen_personal(self):
        self.gender = choice(['Male', 'Female'])
        self.subrace = choice(self.race_table.Subrace.any().split(", "))
        self.languages = self.race_table.Languages.any()
        self.height = rand_meas(self.race_table.Height.any())[self.gender]
        self.weight = rand_meas(self.race_table.Weight.any())[self.gender]
        given = self.data.names.Names[
            (self.data.names.Race == self.race) &
            (self.data.names.Subrace == self.subrace) &
            (self.data.names.Type == self.gender)].any().split(", ")
        if self.race != "Gobber":
            sur = self.data.names.Names[
                (self.data.names.Race == self.race) &
                (self.data.names.Subrace == self.subrace) &
                (self.data.names.Type == "Surname")].any().split(", ")
            self.name = "%s %s" % (LC(given).generate(),
                                   LC(sur).generate())
        else:
            self.name = title_caps(''.join([choice(given)
                                            for _ in range(choice(range(1, 10)))]))
        if self.subrace in ['Khard', 'Skirov', 'Umbrian']:
            if self.gender == "Female":
                self.name = KHARD_SFX.sub("\\1a", self.name)

    def _adjust_race(self):
        if self.race.startswith("Human"):
            self.stats[choice(["PHY", "AGL", "INT"])] += 1
            self._gen_derived_stats()
        elif self.race == "Iosan":
            abil = choice([a for a in
                           self.career_table['All Abilities']
                               .apply(lambda x: x.split(", ")).sum()
                           if a not in self.abilities])
            self.abilities += [abil]
        elif self.race == "Satyxis":
            self.gender = 'Female'
        self.stats[u'DEF'] += int(self.race_table['DEF MOD'])
        self.stats[u'Initiative'] += int(self.race_table['INIT MOD'])
        self.abilities += [c for c in
                           self.race_table['Abilities'].any().split(", ")
                           if c != '-']
        self.ability_table = self.data \
            .abilities[self.data.abilities.Ability.isin(self.abilities)]
        self.benefits += [c for c in self.race_table['Benefits'].tolist() if c != '-']
        self.benefit_table = self.data \
            .benefits[self.data.benefits.Benefit.isin(self.benefits)]

    def apply_xp(self, xp):
        pass

    def write_fdf(self):
        fields = [('Name', 'John Smith'), ('Sex', 'Male')]
        fdf = forge_fdf("", fields, [], [], [])
        fdf_file = open("data.fdf", "wb")
        fdf_file.write(fdf)
        fdf_file.close()


if __name__ == "__main__":

    c = Character()
    print c.summary()
