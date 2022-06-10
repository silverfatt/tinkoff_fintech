import datetime


def is_relevant(caching_time):
    """
    checks if cache exists and relevant
    :param caching_time: datetime object
    :return: True if is relevant and False in opposite
    """
    current_time = datetime.datetime.now()
    seconds = (current_time - caching_time).total_seconds()
    return seconds <= 300
