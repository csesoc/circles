"""
Constructs the course graph using the conditions objects and jumps it as a json file.

From `/backend`, run this as:
    `python3 -m data.processors.cache_graph`

Do NOT run this from it's current location.
"""

from typing import Dict, List, Optional, Tuple

from algorithms.objects.conditions import CompositeCondition
from data.config import GRAPH_CACHE_FILE
from data.processors.load_conditions import construct_conditions_objects
from data.utility.data_helpers import write_data

CONDITIONS: Dict[str, Optional[CompositeCondition]] = construct_conditions_objects()

def cache_graph():
    graph = construct_full_graph()
    write_data(graph, GRAPH_CACHE_FILE)

    return graph

def construct_full_graph():
    # TODO: Other processors should cache a courselist
    # courses: List[str] = CONDITIONS.keys()

    incoming_adj = {
            course: incoming_list(course) for course, cond in CONDITIONS.items()
            if cond is not None
        }

    return {
            "incoming_adjacency_list": incoming_adj,
    }


def incoming_list(course: str) -> List[str]:
    """
    Returns a list of courses which can be used to satisfy 'course'
    eg 2521 -> 1511

    TODO: Integrate this properly as a method in the `Condition` class
    """
    return get_path_from(course)[1]

def get_path_from(course: str) -> Tuple[str, List[str]]:
    """
    fetches courses which can be used to satisfy 'course'
    eg 2521 -> 1511

    Returns a Tuple:
        (
            str : The original course,
            list[str] : The list of courses which can be used to satisfy the original course
        )
    """
    course_condition = CONDITIONS.get(course)

    return course, [
        coursename for coursename, _ in CONDITIONS.items()
        if course_condition and course_condition.is_path_to(coursename)
    ]


if __name__ == "__main__":
    cache_graph()
