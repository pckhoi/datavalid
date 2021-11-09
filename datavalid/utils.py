import os

try:
    TERM_COLS = int(os.popen('stty size', 'r').read().split()[1])
except IndexError:
    TERM_COLS = 100


def indent(s: str, n: int) -> str:
    spaces = ' '*n
    return spaces+s.replace('\n', '\n'+spaces)
