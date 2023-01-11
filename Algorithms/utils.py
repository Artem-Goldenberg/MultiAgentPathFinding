import numpy as np
from CExtension import lightspeed

from Primitives.map import Point
from Primitives.node import Node
from Primitives.solution import Solution
from Primitives.conflict import Conflict, VertexConflict, EdgeConflict

from .mapf import MAPF


def extract_tuple(value) -> tuple:
    if isinstance(value, tuple): return value
    return (value, None)


def get_start_node(task: MAPF, build_mdds=False) -> Node:
    solutions = []
    for i, (s, g) in enumerate(zip(task.start_points, task.goal_points)):
        result = lightspeed.find_path(task.map.cells, s, g, lite_mdd=build_mdds)
        if result is None: 
            return None # type: ignore
        solutions.append(Solution(i, *extract_tuple(result)))
    return Node(solutions)


def update_solution_for(agent_id: int, node: Node, task: MAPF, build_mdd=False) -> bool:
    # construct contiguous ndarrays
    # vc = node.vertexConstraints.get(agent_id, [])
    # ec = node.edgeConstraints.get(agent_id, [])

    vc = filter(lambda c: c.agent_id == agent_id, node.vertexConstraints)
    ec = filter(lambda c: c.agent_id == agent_id, node.edgeConstraints)

    # v_constraints = np.array(
    #     [np.asarray(c) for c in node.vertexConstraints if c.agent_id == agent_id],
    #      dtype=np.int32
    # )
    v_constraints = np.array([np.asarray(c) for c in vc], dtype=np.int32)
    e_constraints = np.array([np.asarray(c) for c in ec], dtype=np.int32)

    s = task.start_points[agent_id]
    g = task.goal_points[agent_id]

    # find path
    result = lightspeed.find_path(
        task.map.cells, s, g, 
        v_constraints=v_constraints, e_constraints=e_constraints,
        lite_mdd=build_mdd
    )

    if result is None: return False

    # update solution
    node.update_solution_for(agent_id, Solution(agent_id, *extract_tuple(result)))

    return True


def simulate(node: Node) -> list[Conflict]:
    """ Given a node with solutions, simulates them to find conflicts """
    conflicts: list[Conflict] = []

    time = 0
    last_step: dict[Point, list[int]] = {}
    current_step: dict[Point, list[int]] = {}
    for time in range(node.time + 1):
        for solution in node.solutions:
            v = solution.get_point_at(time)
            if v in current_step:  # someone in there already
                for other_id in current_step[v]:
                    vc = VertexConflict((solution.agent_id, other_id), time, v)
                    conflicts.append(vc)
                    
                current_step[v].append(solution.agent_id)
            else: 
                current_step[v] = [solution.agent_id]

            if v in last_step:  # someone was there on the previous step
                # can't have more than one agent at the same point by now
                assert len(last_step[v]) == 1

                other_id = last_step[v][0]
                if solution.agent_id == other_id:  # same agent just stayed at this point
                    continue

                previous_point = solution.get_point_at(time - 1)
                # TODO: whacky, fix later
                other_current_point = node.solutions[other_id].get_point_at(time)
                assert node.solutions[other_id].agent_id == other_id
                if other_current_point == previous_point:
                    # some agent was at this point at previous step
                    # and he is now at our previous point
                    # this means we have an edge conflict
                    ec = EdgeConflict(
                        (solution.agent_id, other_id), time - 1, tuple(sorted((previous_point, v)))
                    )
                    conflicts.append(ec)
                    # remove current point of the agent we are 
                    # conflicting with to avoid duplicate conflicts
                    last_step.pop(other_current_point)

        if conflicts: return conflicts

        last_step = current_step
        current_step = {}

    return conflicts


def validate(task: MAPF) -> bool:
    if len(task.start_points) != len(task.goal_points):
        return False

    # assert all starting points and goal points are different
    points = set()
    for (x, y) in task.start_points: 
        p = (x, y) # don't touch
        if p in points: return False
        points.add(p)
    if len(points) != len(task.start_points):
        return False

    points.clear()
    for (x, y) in task.goal_points: 
        p = (x, y)
        if p in points: return False
        points.add(p)
    if len(points) != len(task.goal_points):
        return False

    return True