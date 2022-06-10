from app.database import Film_d


def key_for_rating_top(value: Film_d) -> str:
    return value.average_rating


def key_for_date_top(value: Film_d) -> int:
    return value.release
