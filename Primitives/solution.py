from typing import Optional
from numpy import ndarray
from .map import Point


class Solution:
    """
    Wrapper around agent's path

    - agent_id: agent who has this solution
    - path: agent's path represented as 2d ndarray (rows for vertices, 2 columns for x and y)
    - mdd: optional ndarray, for time `t` `mdd[2 * t]` shows how many nodes are there 
        on the agent MDD's t'th layer, `mdd[2 * t + 1]` shows how many edges are there
        between t'th and (t + 1)'th layer.
    """

    def __init__(self, agent_id: int, path: ndarray, mdd: Optional[ndarray]=None) -> None:
        self.agent_id = agent_id
        self._path = path
        self.cost = len(path) - 1
        self.mdd = mdd

    def get_point_at(self, time: int) -> Point:
        p =  self._path[time if time <= self.cost else -1]
        return p[0], p[1]

    def __repr__(self) -> str:
        return str(self._path)
