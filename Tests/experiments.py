import sys
import os.path
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import signal
import random
import numpy as np
import pandas as pd
from dataclasses import dataclass

from Primitives.map import Map
from Algorithms.mapf import MAPF
from Algorithms import cbs, cbs_pc, cbsh, icbs
from Tests.test import base_test

TIMEOUT = 30 # 5 minutes
MIN_AGENTS = 6
MAX_AGENTS = 7
NUM_INSTANCES = 100

FEATURES = ['time', 'expanded', 'success_rate']
NUM_FEATURES = len(FEATURES)

ALG_NAMES = ['cbs', 'cbs_pc', 'cbsh', 'icbs']
NUM_ALGORITHMS = len(ALG_NAMES)
# final table columns
COLUMNS = pd.MultiIndex.from_product([FEATURES, ALG_NAMES])

# yes, it is an array of modules
# an algorithm is a `solve` function inside each module
ALGORITHMS = [eval(alg) for alg in ALG_NAMES]


def setup():
    map = Map()
    map.read_map(current_dir + "/maps/warehouse.map")
    for k in range(MIN_AGENTS, MAX_AGENTS + 1):
        f = open(f"{current_dir}/maps/tests/{k}.txt", 'w')
        for _ in range(NUM_INSTANCES):
            start_points = random.sample(list(np.argwhere(map.cells == 0)), k)
            goal_points = random.sample(list(np.argwhere(map.cells == 0)), k)
            f.write(f"{k}\n")
            for s, g in zip(start_points, goal_points):
                print(s[0], s[1], g[0], g[1], file=f)
            f.write("\n")
        f.close()


def handle(signum, frame):
    raise TimeoutError("Test ran out of time limit")

signal.signal(signal.SIGALRM, handle)


@dataclass
class AlgorithmStats:
    num_solved: int = 0
    cpu_time: float = 0
    nodes_expanded: float = 0

    def features(self) -> tuple[float, float, float]:
        return (
            self.cpu_time / self.num_solved,
            self.nodes_expanded / self.num_solved,
            self.num_solved / NUM_INSTANCES
        )


def experiment1():
    def mapf_for(k: int, instance: int) -> MAPF:
        with open(current_dir + f"/maps/tests/{k}.txt", 'r') as f:
            lines = f.readlines()

        task = MAPF()
        task.map = m
        task.start_points = np.zeros((k, 2), dtype=int)
        task.goal_points = np.zeros((k, 2), dtype=int)
        for j in range(k):
            sy, sx, gy, gx = map(int, lines[(k + 2) * instance + 1 + j].split())
            task.start_points[j] = (sx, sy)
            task.goal_points[j] = (gx, gy)

        return task

    m = Map()
    m.read_map(current_dir + "/maps/warehouse.map")
    results = np.zeros((MAX_AGENTS - MIN_AGENTS + 1, NUM_ALGORITHMS * NUM_FEATURES))

    for k in range(MIN_AGENTS, MAX_AGENTS + 1):
        stats = [AlgorithmStats() for _ in range(NUM_ALGORITHMS)]
        # 100 instances for each number of agents
        for i in range(NUM_INSTANCES):
            task = mapf_for(k, i)

            for stat, alg in zip(stats, ALGORITHMS):
                signal.alarm(TIMEOUT)

                result, debug = base_test(task, algorithm=alg.solve)

                signal.alarm(0)

                if result is not None:
                    ast, elapsed, wall_time = debug # type: ignore
                    stat.num_solved += 1
                    stat.cpu_time += elapsed
                    stat.nodes_expanded += ast.count_expanded()
                else:
                    assert debug is None
                    print(f"{k} agents, {i} instance")
        
        for i, stat in enumerate(stats):
            if stat.num_solved == 0: continue
            row = k - MIN_AGENTS
            cols = range(i, NUM_ALGORITHMS * NUM_FEATURES, NUM_ALGORITHMS)
            results[row, cols] = stat.features()

        np.save(current_dir + f"/tables/save{k}.npy", arr=results)

    data = pd.DataFrame(results, columns=COLUMNS, index=range(MIN_AGENTS, MAX_AGENTS + 1))
    data.to_csv(current_dir + '/tables/warehouse2.csv')

experiment1()
setup()

def concat():
    results = np.load(current_dir + f"/tables/save7.npy")
    data = pd.DataFrame(results[0:6], columns=COLUMNS, index=range(MIN_AGENTS, MAX_AGENTS + 1))
    data.to_csv(current_dir + '/tables/warehouse.csv') 

# concat()
