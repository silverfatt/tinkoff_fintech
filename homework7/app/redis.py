from redis import Redis  # type: ignore


def get_amount_of_messages_in_redis(redis_client: Redis) -> int:
    return int(redis_client.get('messages'))


def increase_amount_of_messages_in_redis(redis_client: Redis) -> None:
    redis_client.set('messages', f'{get_amount_of_messages_in_redis(redis_client) + 1}')


def add_message_to_redis(redis_client: Redis, client_id: int, data: str) -> None:
    amount = get_amount_of_messages_in_redis(redis_client)
    if amount >= 50:
        amount = 1
    else:
        increase_amount_of_messages_in_redis(redis_client)
    redis_client.set(f'{amount + 1}', str(client_id) + ':' + data)
