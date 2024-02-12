from math import *


def length(c1: tuple, c2: tuple):
    return sqrt(pow(c1[0]-c2[0], 2) + pow(c1[1]-c2[1], 2) + pow(c1[2]-c2[2], 2))

colours: list = [
    (0.3, 0.1, 0.7),
    (1.0, 1.0, 1.0),
    (0.7, 0.45, 0.11),
    (0.1, 0.15, 0.2)
]

for x in colours:
    print(round(length(c1=(0.3, 0.54, 0.24), c2=x), 2))
