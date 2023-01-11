from copy import deepcopy
from .solution import Solution
from .constraint import Constraint, VertexConstraint, EdgeConstraint


class Node:
    """
    Node for the CBS Algorithm

    - vertexConstraints: mapping from agent index to all vertex constraints on that agent, readonly
    - edgeConstraints: mapping from agent index to all edge constraints on that agent, readonly

    - solutions: list of solutions for all agents, readonly, modify using `update_solution_for` method
    - cost: summary cost of all solutions, readonly
    - time: time needed for all agents to complete their paths, just max time over all solutions
    """

    def __init__(self, initial_solutions: list[Solution]) -> None:
        assert initial_solutions
        self.vertexConstraints: frozenset[VertexConstraint] = frozenset()
        self.edgeConstraints: frozenset[EdgeConstraint] = frozenset()

        # self._all_constraints: frozenset[Constraint] = frozenset()

        self.solutions = initial_solutions
        self.cost = sum(map(lambda sol: sol.cost, self.solutions))
        self.time = max(map(lambda sol: sol.cost, self.solutions))

    def make_copy(self, new_constraint: Constraint) -> 'Node':
        node = Node(deepcopy(self.solutions))

        if isinstance(new_constraint, VertexConstraint):
            node.vertexConstraints = self.vertexConstraints.union([new_constraint])
            node.edgeConstraints = self.edgeConstraints
        elif isinstance(new_constraint, EdgeConstraint):
            node.vertexConstraints = self.vertexConstraints
            node.edgeConstraints = self.edgeConstraints.union([new_constraint])
        else:
            raise TypeError("Unexpected Constraint type")

        return node

    def update_solution_for(self, agent_id: int, solution: Solution):
        assert self.solutions[agent_id].agent_id == agent_id
        self.cost -= self.solutions[agent_id].cost
        self.cost += solution.cost
        self.solutions[agent_id] = solution
        self.time = max(map(lambda sol: sol.cost, self.solutions))

    def __hash__(self) -> int:
        # TODO: test hash
        return hash((self.vertexConstraints, self.edgeConstraints))

    def __eq__(self, other) -> bool:
        # TODO: test this as well
        return self.vertexConstraints == other.vertexConstraints \
            and self.edgeConstraints == other.edgeConstraints

    def __lt__(self, other) -> bool:
        # TODO: experiment on this
        return self.cost <= other.cost
