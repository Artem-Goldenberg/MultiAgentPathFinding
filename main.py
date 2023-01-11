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
from Tests.test import test_correctness

test_correctness()

# from Algorithms.mapf import MAPF
# from Algorithms.cbs_pc import find_agents_paths

# # task = MAPF()
# # task.read_txt("Tests/instances/test_47.txt")
# # res = find_agents_paths(task)
# # assert res

# # print(res.cost)

# import numpy as np
# from CExtension.lightspeed import find_path

# mapArray = np.array([
#         [0, 0, 0, 0, 0, 0, 1, 0],
#         [0, 0, 0, 0, 0, 0, 1, 1],
#         [0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 1, 0, 0, 0, 1, 0],
#         [0, 0, 0, 0, 1, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 1, 0],
#         [0, 1, 0, 0, 0, 0, 0, 0]
# ], dtype=np.int8)


# s = (0, 0)
# g = (2, 4)

# ec = np.array([[0, 0, 0, 1, 0]], dtype=np.int32)

# result, countedMdd, mdd = find_path(mapArray, s, g, lite_mdd=True, full_mdd=True)
# print(result, countedMdd)
# for layer in mdd:
#     print(layer)