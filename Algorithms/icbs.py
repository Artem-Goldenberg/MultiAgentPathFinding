from Primitives.node import Node

from .mapf import MAPF
from .cbsh import heuristic
from .cbs_pc import best_conflict
from .search_tree import SearchTreePQS
from .utils import validate, get_start_node, update_solution_for


def solve(task: MAPF):
    """ Improved conflict based search """

    ast = SearchTreePQS()

    if not validate(task): 
        return None, ast

    node = get_start_node(task, counted_mdds=True, mdds=True)
    if node is None: 
        return None, ast

    ast.add_to_open(node)

    while not ast.open_is_empty():  # MAIN LOOP
        node: Node = ast.get_best_node_from_open() # type: ignore
        if node is None: 
            break # open is empty

        conflict = best_conflict(node)
        if conflict is None:  # goal node found
            return node, ast

        for agent_id in conflict.agent_ids: # generate new nodes for 2 agents
            neighbor = node.make_copy(conflict.produce_constraint(agent_id))

            if not ast.was_expanded(neighbor):
                if update_solution_for(agent_id, neighbor, task, counted_mdd=True, mdd=True):
                    neighbor.cost += heuristic(neighbor)
                    ast.add_to_open(neighbor)

        ast.add_to_closed(node)

    return None, ast