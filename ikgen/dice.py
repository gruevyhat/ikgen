#!/usr/bin/python


from random import choice


def die(sides):
    R = range(1, sides+1)

    def roll(dice):
        return sum(choice(R) for i in range(dice))

    return roll


d100 = die(100)
d16 = die(16)
d6 = die(6)
d5 = die(5)
d3 = die(3)

d66 = lambda: (d6(1)*10) + d6(1)
d6_reroll_ones = lambda N: sum((d5(1) + 1) for n in range(N))
d6_drop_lowest = lambda N: sum(sorted(d6(1) for n in range(N))[:N])


if __name__ == "__main__":

    print "3d6, drop the lowest:", d6_drop_lowest(3)
