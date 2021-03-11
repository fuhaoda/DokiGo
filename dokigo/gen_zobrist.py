import random
from dokigo.base import Player, Point


def to_python(player_state):
    if player_state is None:
        return 'None'
    if player_state == Player.black:
        return Player.black
    else:
        return Player.white

MAX63 = 0x7fffffffffffffff

random.seed(0)


table = {}
empty_barod = 0
codes = []
for row in range(1,20):
    for col in range(1,20):
        for state in (Player.black, Player.white, None):
            code = random.randint(1,MAX63)
            table[Point(row, col), state] = code
            codes.append(code)

for code in codes:
    if codes.count(code) > 1:
        print("Hash collision occurred! Please change a different random seed!!")
        input("Press Enter to continue...")

import sys
original_stdout = sys.stdout

with open('zobrist.py', 'w') as outfile:
    sys.stdout = outfile
    print('from dokigo.base import Player, Point')
    print('')
    print("__all__ = ['HASH_CODE', 'EMPTY_BOARD']")
    print('')
    print('HASH_CODE = {')
    for (pt, state), hash_code in table.items():
        print(' (%r, %s):%r,' %(pt, to_python(state), hash_code))
    print('}')
    print('')
    print('EMPTY_BOARD = %d' % (empty_barod))