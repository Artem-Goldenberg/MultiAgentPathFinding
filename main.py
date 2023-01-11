import argparse

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
    '-a', '--animate',
    action='store_true',
    help="animate the solution"
)

# parser.print_help()
# args = parser.parse_args()

# print(args)

import Algorithms.cbs

from Algorithms.mapf import MAPF
from Algorithms.cbs_pc import find_agents_paths

task = MAPF()
task.read_txt("Tests/instances/test_47.txt")
res = find_agents_paths(task)
assert res

print(res.cost)

# import numpy as np

# mapArray = np.array([
#         [0, 0, 0, 0, 0, 0, 0, 1],
#         [0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 1, 0, 0, 0, 1, 0],
#         [0, 0, 0, 0, 1, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 1, 0],
#         [0, 1, 0, 0, 0, 0, 0, 0]
# ], dtype=np.int8)

# from CExtension.lightspeed import find_path

# s = (1, 5)
# g = (5, 7)

# ec = np.array([[0, 1, 5, 2, 5]], dtype=np.int32)

# result = find_path(mapArray, s, g, e_constraints=ec)
# print(result)