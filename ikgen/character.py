#!/usr/bin/env python


"""
Primary class for IKRPG character generation.

author: GVH
version: 0.0.1
"""

# TODO: Assets, MAT, RAT
# TODO: Write FDF output for PDF generation.

import os
import re
import json
import pandas as pd
import numpy as np
from random import choice
from collections import defaultdict, Counter
from fdfgen import forge_fdf


SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

SKILL = re.compile("(?!<: )([A-Z][^,:]+?) ([0-9])")
CHOOSE_N = re.compile("Choose (?:one|two|three): (.*)")
KHARD_SFX = re.compile("([^aeiou])$")
MEAS = re.compile("(\d+)-(\d+) (?:in|lb)")

ARCHETYPES = [u'Gifted', u'Intellectual', u'Mighty', u'Skilled']
STATS = [u'PHY', u'SPD', u'STR', u'AGL', u'PRW', u'POI', u'INT', u'ARC', u'PER']
LEVELS = {'Hero': 2, 'Veteran': 4, 'Epic': 6}
GENERAL_SKILLS = ['Animal Handling', 'Climbing', 'Detection', 'Driving',
    'Gambling', 'Intimidation', 'Jumping', 'Riding', 'Swimming',
    'Lore (Extraordinary Zoology)', 'Lore (Morrowan)', 'Lore (Ancient History)',
    'Lore (Urcaen Lore)', 'Lore (Infernal)', 'Lore (Draconic)', 'Lore (Nation)']

def sumdict(list_of_dicts):
    c = defaultdict(int)
    for d in list_of_dicts:
        for k, v in d.iteritems():
            c[k] += v
    return c


def maxdict(list_of_dicts):
    c = defaultdict(int)
    for d in list_of_dicts:
        for k, v in d.iteritems():
            c[k] = max(c[k], v)
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


def uniq(L):
    return [l for i, l in enumerate(L) if l not in L[:i]]


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


def combine_values(L):
    return ', '.join(["%s (x%d)" % (k, v)
                      for k, v in Counter(L).items()])

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

    def __init__(self, race=None, stats=None,
                 archetype=None, benefits=None,
                 careers=None, spells=None, abilities=None,
                 connections=None, money=None,
                 assets=None, xp=0, chardata=None):
        self.race = race or None
        self.archetype = archetype or None
        self.benefits = benefits or []
        self.fixed_stats = stats or {}
        self.careers = careers or []
        self.spells = spells or []
        self.money = money or 0
        self.assets = assets or []
        self.connections = connections or []
        self.abilities = abilities or []
        self.level = 'Hero'
        self.data = chardata or CharData()
        self.build()
        self.apply_xp(xp)

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
        stats += ['Level: %s (%d XP)' % (self.level, self.xp)]
        stats += ["Stats: PHY %(PHY)d, SPD %(SPD)d, STR %(STR)d" % self.stats]
        stats += ["       AGL %(AGL)d, PRW %(PRW)d, POI %(POI)d" % self.stats]
        stats += ["       INT %(INT)d, ARC %(ARC)d, PER %(PER)d" % self.stats]
        stats += ["       DEF %(DEF)d, ARM %(ARM)d, Init %(Initiative)d" % self.stats]
        stats += ["       Cmd %(Command)d, Will %(Willpower)d" % self.stats]
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
        if self.armor:
            stats += ["Armor:\n" + self.armor_table.to_string(index=False)]
        if self.weap:
            stats += ["Weapons:\n" + self.weap_table.to_string(index=False)]
        if self.spells:
            stats += ["Spells:\n" + self.spell_table.to_string(index=False)]
        if self.connections:
            stats += ["Connections: " + combine_values(self.connections)]
        if self.assets:
            stats += ["Assets: " + ", ".join(self.assets)]
        stats += ["GC: " + str(self.money)]
        return "\n".join(stats)

    def to_json(self, fn=None):
        D = {"Name": self.name}
        if self.subrace != '-':
            D.update({"Race": self.race})
        else:
            D.update({"Race": self.race})
        D.update({"Gender": self.gender})
        D.update({"Measurements": {"height": self.height,
                                   "weight": self.weight}})
        D.update({"Careers": ", ".join(self.careers)})
        D.update({"Archetype": self.archetype})
        D.update({"Level": "%s (%d XP)" % (self.level, self.xp)})
        D.update({"Stats": self.stats})
        D.update({"Benefits": self.benefit_table[['Benefit', 'Description']]
                 .apply(lambda x: "%s: %s" % (x.iloc[0], x.iloc[1]), axis=1)
                 .tolist()})
        D.update({"Abilities": self.ability_table[['Ability', 'Short Description']]
                 .apply(lambda x: "%s: %s" % (x.iloc[0], x.iloc[1]), axis=1)
                 .tolist()})
        D.update({"Military Skills": self.skills_mil})
        D.update({"Occupational Skills": self.skills_occ})
        D.update({"Languages": self.languages})
        if self.armor:
            D.update({"Armor": self.armor_table.to_records(index=False).tolist()})
        if self.weap:
            D.update({"Weapons": self.weap_table.to_records(index=False).tolist()})
        if self.spells:
            D.update({"Spells": self.spell_table.to_records(index=False).tolist()})
        if self.connections:
            D.update({"Connections": self.connections})
        if self.assets:
            D.update({"Assets": self.assets})
        D.update({"GC": self.money})
        if fn:
            with open(fn, "w") as fo:
                json.dump(D, fo)
        else:
            return json.dumps(D, sort_keys=True, indent=4)

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
        self._gen_weap()
        self._gen_armor()
        self._calc_derived_stats()
        self._adjust_race()
        self._adjust_careers()

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
        # Limit by race
        self.career_mask = self.data.careers[self.race] == 1
        # Limit for archetype
        if self.archetype != "Gifted":
            self.career_mask &= self.data.careers.Gifted == 0
        if self.archetype != "Mighty":
            self.career_mask &= self.data.careers.Mighty == 0
        # Choose careers
        for i in range(2):
            try:
                self._add_career(self.careers[i])
            except:
                self._add_career()
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

    def _add_career(self, career=None):
        if career:
            new_career = self.data.careers[self.data.careers.Career == career]
        else:
            careers = self.data.careers[self.career_mask]
            new_career = careers[~careers.Career.isin(self.careers)].sample()
        restr = [c for c in new_career['Career Restrictions'].any().split(', ')
                 if c != '-']
        if restr and set(self.careers) \
                .difference(new_career.Career.tolist()) \
                .difference(restr):
            self._add_career()
        else:
            basename = new_career.Career.any().split()[0]
            self.career_mask &= ~self.data.careers.Career \
                .apply(lambda x: x.startswith(basename))
            if restr:
                self.career_mask &= self.data.careers.Career.isin(restr)
            try:
                self.career_table = pd.concat([self.career_table, new_career])
            except:
                self.career_table = new_career
            self.careers = uniq(self.careers + [new_career.Career.any()])

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
            self._add_stat()
        if self.fixed_stats:
            self.stats.update(self.fixed_stats)

    def _add_stat(self):
        stat = choice_geom(self.archetype_table['Stat Order'].any().split(", "),
                           float(self.archetype_table['p']))
        limit = self.stat_table[self.stat_table.Set == self.level][stat] \
            .iloc[0]
        if self.stats[stat] < limit:
            self.stats[stat] += 1
        else:
            self._add_stat()

    def _calc_derived_stats(self):
        self.stats[u'DEF'] = sum(self.stats[s] for s in ['AGL', 'SPD', 'PER'])
        self.stats[u'ARM'] = self.stats['PHY']
        self.stats[u'Initiative'] = sum(self.stats[s] for s in ['PRW', 'SPD', 'PER'])
        self.stats[u'Command'] = self.stats['INT']
        self.stats[u'Willpower'] = self.stats['INT'] + self.stats['PHY']
        if 'Command' in self.skills_occ.keys():
            self.stats[u'Command'] += int(self.skills_occ['Command'])

    def _gen_spells(self):
        if self.archetype == "Gifted":
            spells = ', '.join(self.career_table['Starting Sp']).split(', ')
            self.spell_table = self.data \
                .spells[self.data.spells.Spell.isin(spells)]
            self.spells = list(set(self.spells + self.spell_table.Spell.tolist()))

    def _gen_connections(self):
        conns = [c for c in
                 self.career_table['Starting Conns'].tolist()
                 if c != 'None']
        self.connections += conns

    def _gen_assets(self):
        assets = [a for a in
                  self.career_table.Assets.tolist()
                  if a != "-"]
        if assets:
            self.assets = list(set(self.assets + assets))

    def _gen_money(self):
        money = self.career_table.GC.sum()
        if money:
            self.money += money

    def _gen_weap(self):
        assets = ''.join(self.assets).lower()
        weaps = [w for w in self.data.weapons.Weapon.tolist()
                 if assets.find(w.lower()) > -1]
        if not weaps:
            best_skill = choice([k for k, v in self.skills_mil.items()
                                 if v == max(self.skills_mil.values())])
            avail = self.data.weapons.Weapon[(self.data.weapons.Skill == best_skill)
                                             & (self.data.weapons.Cost <= self.money)].tolist()
            avail = [a for a in avail if a not in weaps]
            new_weapon = choice_geom(avail, 0.3)
            weaps += [new_weapon]
            self.money -= self.data.weapons[self.data.weapons.Weapon == new_weapon].Cost.tolist()[0]
        self.weap_table = self.data.weapons[self.data.weapons.Weapon.isin(weaps)]
        self.weap = self.weap_table.Weapon.tolist()

    def _gen_armor(self):
        string_match = self.data.armor.Armor \
            .apply(lambda x: self.career_table.Assets.sum().lower().find(x.lower()) > -1)
        self.armor_table = self.data.armor[string_match]
        if len(self.armor_table) == 0 and self.money >= 25:
            self.armor_table = self.data.armor[self.data.armor.Armor == "Armored Great Coat"]
            self.money -= 25
        if 'Shield' in self.skills_mil.keys() \
                and 'Shield' not in self.armor_table.Armor.tolist() \
                and self.money >= 20:
            self.armor_table = pd.concat([self.armor_table,
                                          self.data.armor[self.data.armor.Armor == "Shield"]])
            self.money -= 20
        self.armor = self.armor_table.Armor.tolist()

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
            self._calc_derived_stats()
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

    def _adjust_careers(self):
        if self.career_table.Career.apply(lambda x: x.startswith("Warcaster")).any():
            limit = self.stat_table[self.stat_table.Set == self.level]['ARC'] \
                .iloc[0]
            if self.stats['ARC'] < limit:
                self.stats['ARC'] += 1
            else:
                self._add_stat()

    def apply_xp(self, xp=None):
        if xp >= 50:
            self.level = "Veteran"
        if xp >= 100:
            self.level = "Epic"
        self.xp, occ, sacm, stat, ben, ben_or_car = self.data.xp.loc[xp].tolist()
        if occ > 0:
            for _ in range(occ):
                self._add_occ()
        if sacm > 0:
            for _ in range(sacm):
                sacm_fncs = [self._add_abil, self._add_conn]
                if any(v < LEVELS[self.level] for v in self.skills_mil.values()):
                    sacm_fncs += [self._add_mil]
                if self.spells \
                        and len(self.spell_table) < 2 * self.stats['INT']:
                    sacm_fncs += [self._add_spell]
                choice(sacm_fncs)()
        if stat > 0:
            for _ in range(stat):
                self._add_stat()
        if ben > 0:
            for _ in range(ben):
                self._add_ben()
        if ben_or_car > 0:
            if choice(range(2)) == 0:
                self._add_career()
                self._add_occ()
                self._add_occ()
            else:
                self._add_ben()
        self._calc_derived_stats()

    def _add_ben(self):
        benefits = self.data.benefits[self.data.benefits.Archetype == self.archetype]
        new_benefit = benefits[~benefits.Benefit.isin(self.benefits)].sample()
        self.benefit_table = pd.concat([self.benefit_table, new_benefit])
        self.benefits = self.benefit_table.Benefit.tolist()

    def _add_spell(self):
        spell_lists = [l for l in
                       self.career_table['All Sp'].apply(lambda x: x.split(", ")).sum()
                       if l != "-"]
        all_spells = [x for y in
                      [self.data.spell_lists[s]
                       .apply(lambda x: x.split(", ")).sum()
                       for s in spell_lists]
                      for x in y]
        new_spell = choice([s for s in all_spells if s not in
                          self.spell_table.Spell.tolist()])
        self.spell_table = pd.concat([self.spell_table,
                                      self.data.spells[self.data.spells.Spell == new_spell]])

    def _add_abil(self):
        all_abils = self.career_table['All Abilities'] \
            .apply(lambda x: x.split(", ")).sum()
        new_abil = choice([a for a in all_abils if a not in
                           self.ability_table.Ability.tolist()])
        self.ability_table = pd.concat([self.ability_table,
                                        self.data.abilities[self.data.abilities.Ability == new_abil]])

    def _add_conn(self):
        self.conns = self.career_table['All Conns'].apply(lambda x: x.split(', ')).sum()
        new_conn = choice(self.conns)
        if new_conn != "None":
            self.connections += [new_conn]
        else:
            if choice(range(2)) == 0:
                self._add_occ()
            else:
                self._add_mil()

    def _add_occ(self):
        skill_limits = maxdict(self.career_table["All Occ"]
                               .apply(parse).tolist() + [self.skills_occ])
        skill = choice(skill_limits.keys())
        if self.skills_occ.get(skill, 0) < min(skill_limits[skill],
                                               LEVELS[self.level]):
            if skill == "General Skills":
                skill = choice(GENERAL_SKILLS)
            self.skills_occ[skill] += 1
        else:
            self._add_occ()

    def _add_mil(self):
        skill_limits = maxdict(self.career_table["All Military"]
                               .apply(parse).tolist() + [self.skills_mil])
        skill = choice(skill_limits.keys())
        if self.skills_mil[skill] < min(skill_limits[skill],
                                        LEVELS[self.level]):
            self.skills_mil[skill] += 1
        else:
            self._add_mil()

    def write_fdf(self):
        fields = [('Name', 'John Smith'), ('Sex', 'Male')]
        fdf = forge_fdf("", fields, [], [], [])
        fdf_file = open("data.fdf", "wb")
        fdf_file.write(fdf)
        fdf_file.close()


if __name__ == "__main__":

    #c = Character(archetype="Gifted", careers=['Warcaster', 'Cutthroat'], race="Human (Khadoran)", xp=150)
    c = Character(archetype="Skilled", careers=['Trencher', 'Ranger'], race="Human (Cygnaran)")
    #c = Character(xp=10)
    print c.summary()
    #print c.to_json()
