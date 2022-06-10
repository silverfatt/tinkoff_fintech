from mock import patch  # type: ignore

from app.app import format_last_messages


def test_last_messages(client):
    with patch('app.app.format_last_messages') as mock:
        mock.return_value = 'fwqfq'
        response = client.get('/last_messages')
        assert response.status_code == 200


def test_format_last_messages(fake_redis_client):
    fake_redis_client.set('messages', '1')
    fake_redis_client.set('1', 'User123:Hello')
    assert format_last_messages(fake_redis_client) == '|  From User123:Hell:   |'
