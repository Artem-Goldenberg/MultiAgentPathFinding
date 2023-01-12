import itertools
from operator import attrgetter
from collections import Counter

from Primitives.node import Node
from Primitives.conflict import Conflict, VertexConflict, EdgeConflict

from .mapf import MAPF
from .search_tree import SearchTreePQS
from .utils import validate, simulate, get_start_node, update_solution_for


def solve_lazy(task: MAPF):
    """ Conflict based search with prioritizing conflicts optimization lazy mdd building """

    ast = SearchTreePQS()

    if not validate(task): 
        return None, ast

    node = get_start_node(task)
    if node is None: 
        return None, ast

    ast.add_to_open(node)

    while not ast.open_is_empty():  # MAIN LOOP
        node: Node = ast.get_best_node_from_open() # type: ignore
        if node is None: break # open is empty

        conflict = best_conflict_lazy(node, task)
        # conflict = simple_best(node, task)
        if conflict is None:  # goal node found
            return node, ast

        for agent_id in conflict.agent_ids: # generate new nodes for 2 agents
            neighbor = node.make_copy(conflict.produce_constraint(agent_id))

            if not ast.was_expanded(neighbor):
                if update_solution_for(agent_id, neighbor, task):
                    assert neighbor.cost >= node.cost
                    ast.add_to_open(neighbor)

        ast.add_to_closed(node)

    return None, ast


def solve(task: MAPF):
    """ Conflict based search with prioritizing conflicts optimization and not lazy """

    ast = SearchTreePQS()

    if not validate(task): return None, ast

    node = get_start_node(task, counted_mdds=True)
    if node is None: return None, ast

    ast.add_to_open(node)

    while not ast.open_is_empty():  # MAIN LOOP
        node: Node = ast.get_best_node_from_open() # type: ignore
        if node is None: break # open is empty

        conflict = best_conflict(node)
        # conflict = simple_best(node)
        if conflict is None:  # goal node found
            return node, ast

        for agent_id in conflict.agent_ids: # generate new nodes for 2 agents
            neighbor = node.make_copy(conflict.produce_constraint(agent_id))

            if not ast.was_expanded(neighbor):
                if update_solution_for(agent_id, neighbor, task, counted_mdd=True):
                    assert neighbor.cost >= node.cost
                    ast.add_to_open(neighbor)

        ast.add_to_closed(node)

    return None, ast


# TODO: delete
def simple_best(node: Node, task: MAPF) -> Conflict:
    def get_mdd(agent_id: int):
        cmdd = node.solutions[agent_id].counted_mdd
        assert cmdd is not None
        if cmdd is None:
            update_solution_for(agent_id, node, task, counted_mdd=True)
            cmdd = node.solutions[agent_id].counted_mdd
            assert cmdd.size # type: ignore
        return cmdd 

    def thin(cmdd, layer: int) -> bool:
        if layer < cmdd.size:
            return cmdd[layer] == 1
        return True
    
    conflicts = simulate(node)
    if not conflicts: return None # type: ignore

    semi_cardinal = None
    for conflict in conflicts:
        mdd1, mdd2 = map(get_mdd, conflict.agent_ids)

        if isinstance(conflict, VertexConflict):
            layer = conflict.time * 2
        elif isinstance(conflict, EdgeConflict):
            layer = conflict.time * 2 + 1
        else:
            raise TypeError("Unexpected Conflict type")

        if thin(mdd1, layer) and thin(mdd2, layer):
            return conflict
        elif thin(mdd1, layer) or thin(mdd2, layer):
            semi_cardinal = conflict

    if semi_cardinal is not None: return semi_cardinal
    return conflicts[0]


def best_conflict(node: Node) -> Conflict:
    def get_mdd(agent_id: int):
        return node.solutions[agent_id].counted_mdd
    
    def conflict_priority(c: Conflict):
        return agents_priority[c.agent_ids[0]] + agents_priority[c.agent_ids[1]]
    
    def thin(mdd, layer: int) -> bool:
        if layer < mdd.size:
            return mdd[layer] == 1
        return True

    conflicts = simulate(node)
    if not conflicts: return None # type: ignore

    # order conflicts by priority of their agents and iterate through them,
    # trying to find cardinal conflict
    agents_priority = Counter(
        itertools.chain.from_iterable(map(attrgetter('agent_ids'), conflicts))
    )

    semi_cardinal = None
    for conflict in sorted(conflicts, key=conflict_priority, reverse=True):
        mdd1, mdd2 = map(get_mdd, conflict.agent_ids)

        if isinstance(conflict, VertexConflict):
            layer = conflict.time * 2
        elif isinstance(conflict, EdgeConflict):
            layer = conflict.time * 2 + 1
        else:
            raise TypeError("Unexpected Conflict type")

        if thin(mdd1, layer) and thin(mdd2, layer):
            return conflict
        elif thin(mdd1, layer) or thin(mdd2, layer):
            semi_cardinal = conflict

    if semi_cardinal is not None: return semi_cardinal
    return conflicts[0]


def best_conflict_lazy(node: Node, task: MAPF) -> Conflict:
    def get_mdd(agent_id: int):
        cmdd = node.solutions[agent_id].counted_mdd
        if cmdd is None:
            update_solution_for(agent_id, node, task, counted_mdd=True)
            cmdd = node.solutions[agent_id].counted_mdd
            assert cmdd.size # type: ignore
        return cmdd
    
    def conflict_priority(c: Conflict):
        return agents_priority[c.agent_ids[0]] + agents_priority[c.agent_ids[1]]
    
    def thin(mdd, layer: int) -> bool:
        if layer < mdd.size:
            return mdd[layer] == 1
        return True

    conflicts = simulate(node)
    if not conflicts: return None # type: ignore

    # order conflicts by priority of their agents and iterate through them,
    # trying to find cardinal conflict
    agents_priority = Counter(
        itertools.chain.from_iterable(map(attrgetter('agent_ids'), conflicts))
    )

    semi_cardinal = None
    for conflict in sorted(conflicts, key=conflict_priority, reverse=True):
        mdd1, mdd2 = map(get_mdd, conflict.agent_ids)

        if isinstance(conflict, VertexConflict):
            layer = conflict.time * 2
        elif isinstance(conflict, EdgeConflict):
            layer = conflict.time * 2 + 1
        else:
            raise TypeError("Unexpected Conflict type")

        if thin(mdd1, layer) and thin(mdd2, layer):
            return conflict
        elif thin(mdd1, layer) or thin(mdd2, layer):
            semi_cardinal = conflict

    if semi_cardinal is not None: return semi_cardinal
    return conflicts[0]
