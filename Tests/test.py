import sys
import time
import shutil
import os.path
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import pandas as pd
from tqdm import tqdm
from inspect import getmodule
from typing import Callable, Optional

from Primitives.node import Node
from Algorithms.mapf import MAPF
from Algorithms.search_tree import SearchTreePQS as ST

import Tests.utils as utils
from Tests.graphics import animate_solutions

import Algorithms.cbs as cbs

# Should be universal type for all CBS-like algorithms
Solver = Callable[[MAPF], tuple[Optional[Node], ST]]
DebugInfo = tuple[ST, float, float] # Search tree, cpu time, wall time


def copy_solution_file(tmp_file: str):
    filename = "solutions.gif"
    i = 1
    while os.path.isfile(filename):
        filename = f"solutions{i}.gif"
        i += 1

    shutil.copyfile(tmp_file, "./saved/" + filename)


def base_test(task: MAPF, algorithm: Solver, *, show=False, save=None) -> tuple[Optional[Node], Optional[DebugInfo]]:
    """
    This function designed to be the base testing function for all CBS-like algorithms
    
    It means that in order to test any CBS-like algorithm you should call this function, providing 
    you algorithm as this functions's `algorithm`

    - task: MAPF task to test the algorithm on
    - algorithm: Callable function which returns the node as it's final result
    - show: boolean flag indicating if we need to draw an animated solution to this test
    - save: optional string, path to save .gif file, default is `None` (don't save) 
    """

    try:
        start_cpu_time = time.process_time()
        start_wall_time = time.time()
        result, ast = algorithm(task)
        wall_time = time.time() - start_wall_time
        cpu_time = time.process_time() - start_cpu_time
    except Exception as e:
        print(f"Exception while executing: {e}")
        return None, None

    if result is None or (not show and not save):
        return result, (ast, cpu_time, wall_time)
    
    if save: print(f"Saving solution animation to '{save}'")
    animate_solutions(task.map, result, show=show, save=save)

    return result, (ast, cpu_time, wall_time)


def test_correctness(algorithm: Solver = cbs.solve, can_fail_before_quit=10):
    """ 
    Validate correctness of an algorithm by comparing its solutions to the precomputed ones
    
    - algorithm: CBS algorithm to test
    - can_fail_before_quit: number of failed tests allowed before quiting this test
        It's just for debugging purposes, if your algorithm failed at least one test, 
        then it's incorrect no matter what the value of this property, just not to give any false hopes....
    """
    print(
        f"Testing '{getmodule(algorithm).__name__}.{algorithm.__name__}' for the correctness: "  # type: ignore
    )
    failed = 0
    answers = pd.read_csv(current_dir + "/instances/min-sum-of-cost.csv")
    for i, (name, cost) in tqdm(answers.iterrows()):
        task = MAPF()
        task.read_txt(current_dir + '/' + name)
        result, _ = base_test(task, algorithm)
        if result is None or result.cost != cost:
            found_cost = result.cost if result is not None else '∞'
            print(
                f"❌❌❌ 😰 Fail on test {i + 1}: "  # type: ignore
                f"cost found = {found_cost} ≠ {cost}, "
                f"file: {name} ❌❌❌"
            )
            failed += 1
            if failed >= can_fail_before_quit:
                print("\nToo many failed cases 😩, breaking the test 😡")
                return

    if failed == 0:
        print(
            "️✅✅️✅ Congratulations! 🤩 Your algorithm has passed all tests! 😎😎😎"
        )


def simple_test(filename: str, algorithms: list[Solver] = [cbs.solve], show=True, save=None, print_path=False):
    """ 
    Tests algorithms (one or multiple) on one test, giving maximum information 

    - filename: name of the test file in .txt format (as always), 
        filename MUST be relative to the `Tests` directory
    - algorithms: list of all algorithms to test, default is the standard cbs algorithm
    - show: boolean flag indicating whether or not to draw animated solution, it may take some time
    - save: optional string, path to save .gif file, default is `None` (don't save) 
    """

    task = MAPF()
    # task.read_txt(current_dir + '/' + filename)
    task.read_txt('./' + filename)

    for algorithm in algorithms:
        print(
            f"\nTesting '{getmodule(algorithm).__name__}.{algorithm.__name__}' " # type: ignore
            f"algorithm on the map '{filename}':"
        )
        result, debug = base_test(task, algorithm, show=show, save=save)
        if result is None:
            print("\nPath not fount!")
            continue
        print(f"\nFound solution with cost = {result.cost}")
        if debug is not None:
            ast, cpu_time, wall_time = debug
            print(f"Expanded nodes: {ast.count_expanded()}")
            print(f"CPU time = {cpu_time} seconds, Wall time = {wall_time} seconds")
            if print_path: utils.print_path(result)
        print("------------------------------------------------------------------------------------------------\n")

