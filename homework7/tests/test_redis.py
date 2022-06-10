from app.redis import add_message_to_redis


def test_add_message_to_redis(fake_redis_client):
    fake_redis_client.set('messages', '0')
    add_message_to_redis(fake_redis_client, 123, 'Hello')
    assert fake_redis_client.get('1') == b'123:Hello'


def test_add_message_to_full_redis(fake_redis_client):
    fake_redis_client.set('messages', '50')
    add_message_to_redis(fake_redis_client, 123, 'Hello')
    assert fake_redis_client.get('1') == b'123:Hello'
