import math
from typing import List, Optional, Tuple

from app.datab import History, Values


def get_name_and_amount(command: str) -> Tuple[str, int]:
    """
    gets name and amount from a string like Alphacoin 4
    :param command: example: Alphacoin 4
    :return: pair of values: (Alphacoin, 4)
    """
    name_and_amount = command.split()
    return name_and_amount[0], int(name_and_amount[1])


def paginate(
    number_of_posts: int, page: str, h: List[History]
) -> Tuple[List[History], Optional[int], int]:
    page = int(page) if page else 1  # type: ignore
    allPosts = h
    allPosts.reverse()
    history_length = len(allPosts)
    allPosts = allPosts[
        (page - 1) * number_of_posts : page * number_of_posts  # type: ignore
    ]  # type: ignore
    prev = page - 1 if page > 1 else None  # type: ignore
    next_ = page + 1 if page < math.ceil(history_length / number_of_posts) else None  # type: ignore
    return allPosts, prev, next_


def compare_lists(list1: List[Values], list2: List[Values]) -> bool:
    for i in range(len(list1)):
        if list1[i].value != list2[i].value:
            return False
    return True
