import numpy as np
import networkx as nx

from Primitives.node import Node

from .mapf import MAPF
from .search_tree import SearchTreePQS
from .utils import validate, simulate, get_start_node, update_solution_for


def solve(task: MAPF):
    """ Conflict based search using admissable heuristic """

    ast = SearchTreePQS()

    if not validate(task): return None, ast

    node = get_start_node(task, mdds=True)
    if node is None: return None, ast

    ast.add_to_open(node)

    while not ast.open_is_empty():  # MAIN LOOP
        node: Node = ast.get_best_node_from_open() # type: ignore
        if node is None: break # open is empty

        conflicts = simulate(node)
        if not conflicts:  # goal node found
            return node, ast

        conflict = conflicts[0]

        for agent_id in conflict.agent_ids: # generate new nodes for 2 agents
            neighbor = node.make_copy(conflict.produce_constraint(agent_id))

            if not ast.was_expanded(neighbor):
                if update_solution_for(agent_id, neighbor, task, mdd=True):
                    h = heuristic(neighbor)
                    neighbor.cost += h # CBS-h
                    # assert neighbor.cost >= node.cost, "child cost must be >= parent cost"
                    ast.add_to_open(neighbor)

        ast.add_to_closed(node)

    return None, ast


def heuristic(node: Node) -> int:
    def get_mdd(agent_id: int) -> list[np.ndarray]:
        return node.solutions[agent_id].mdd # type: ignore

    conflict_graph = nx.Graph()
    num_agents = len(node.solutions)

    for outer_agent in range(num_agents):
        for inner_agent in range(outer_agent + 1, num_agents):
            mdd1 = get_mdd(outer_agent)
            mdd2 = get_mdd(inner_agent)

            # TODO: delete
            assert mdd1
            assert mdd2

            for layer1, layer2 in zip(mdd1, mdd2):
                if layer1.shape[0] == layer2.shape[0] == 1:
                    if layer1[0, 0] == layer2[0, 0] and layer1[0, 1] == layer2[0, 1]:
                        conflict_graph.add_edge(inner_agent, outer_agent)

    for k in range(1, conflict_graph.number_of_nodes()):
        if k_vertex_cover(conflict_graph, k):
            return k
    return 0


def k_vertex_cover(g, k):
    if g.number_of_edges() == 0:
        return True
    elif g.number_of_edges() > k*g.number_of_nodes():
        return False
        
    v = list(g.edges())[0]
    g1 = g.copy()
    g2 = g.copy()

    g1.remove_node(v[0])
    g2.remove_node(v[1])
    return k_vertex_cover(g1, k-1) or k_vertex_cover(g2, k-1)
