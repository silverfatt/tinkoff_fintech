from typing import Any, Dict, List

from app.database import Film_d


def paginate(
    item: List[Dict[Any, Any]], per_page: int, page: int
) -> List[Dict[Any, Any]]:
    page = int(page) if page else 1  # type: ignore
    page = max(page, 1)
    if per_page < 1:
        per_page = 10
    paginated = item[(page - 1) * per_page : page * per_page]
    return paginated


def makelist(q: List[Film_d]) -> List[Dict[Any, Any]]:
    films = []
    for a in q:
        film = {
            'title': a.title,
            'director': a.director,
            'release': a.release,
            'average_rating': a.average_rating,
        }
        films.append(film)
    return films
