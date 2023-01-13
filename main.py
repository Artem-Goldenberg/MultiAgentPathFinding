import argparse

from Algorithms import cbs, cbs_pc, cbsh, icbs
from Tests.test import simple_test

parser = argparse.ArgumentParser(
    description="Access different algorithms for multi-agent path finding problem",
    epilog="For more, see https://github.com/Artem-Goldenberg/MultiAgentPathFinding"
)
parser.add_argument(
    'algorithm',
     choices=['cbs', 'cbs_pc', 'cbsh', 'icbs'],
     help="algorithm to solve your problem with"
)
parser.add_argument(
    'filename',
    help="path to file with a MAPF problem"
)
parser.add_argument(
    '-d', '--draw',
    nargs='?',
    const='solution_animation.gif',
    metavar="filepath",
    help="store the solution animation in specified path, defaults 'solution_animation.gif'"
)

args = parser.parse_args()

simple_test(
    args.filename, 
    algorithms=[eval(args.algorithm + '.solve')],
    show=False, save=args.draw, print_path=True
)
