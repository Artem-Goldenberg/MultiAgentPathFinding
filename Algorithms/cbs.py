from Primitives.node import Node

from .mapf import MAPF
from .search_tree import SearchTreePQS
from .utils import validate, simulate, get_start_node, update_solution_for


def solve(task: MAPF):
    """ Base version of the conflict based search """

    ast = SearchTreePQS()

    if not validate(task): return None, ast

    node = get_start_node(task)
    if node is None: return None, ast

    ast.add_to_open(node)

    while not ast.open_is_empty():  # MAIN LOOP
        node: Node = ast.get_best_node_from_open() # type: ignore
        if node is None: break # open is empty

        conflicts = simulate(node)
        if not conflicts:  # goal node found
            return node, ast

        conflict = conflicts[0]  # base version without any improvements

        for agent_id in conflict.agent_ids: # generate new nodes for 2 agents
            neighbor = node.make_copy(conflict.produce_constraint(agent_id))

            if not ast.was_expanded(neighbor):
                if update_solution_for(agent_id, neighbor, task):
                    assert neighbor.cost >= node.cost
                    ast.add_to_open(neighbor)

        ast.add_to_closed(node)

    return None, ast
