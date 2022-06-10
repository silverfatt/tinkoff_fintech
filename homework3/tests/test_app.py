from http import HTTPStatus

import pytest

from app.app import (
    add_element_to_active_tasks,
    app,
    change_type_of_list,
    search,
    search_substring,
)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_change_type_of_list():
    assert change_type_of_list('Active') == 'active'
    assert change_type_of_list('Completed') == 'completed'
    assert change_type_of_list('Show All') == 'all'
    assert change_type_of_list('eqfqwgqgq') == 'active'


def test_base_get(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK


def test_base_post(client):
    response = client.post('/')
    assert response.status_code == HTTPStatus.OK


def test_change_list(client):
    response = client.post('/change_list')
    assert response.status_code == HTTPStatus.FOUND


def test_add(client):
    response = client.post('/add')
    assert response.status_code == HTTPStatus.FOUND


def test_search():
    assert search('a', [], ['awa']) == ['Completed: awa']


def test_search_substring(client):
    client.post('/search_substring')
    assert search_substring().status_code == HTTPStatus.FOUND


def test_clear(client):
    response = client.post('/clear')
    assert response.status_code == HTTPStatus.FOUND


def test_remove(client):
    response = client.post('/remove')
    assert response.status_code == HTTPStatus.FOUND


def test_add_element_to_active_tasks():
    active_tasks = ['a']
    assert add_element_to_active_tasks('', active_tasks) == ''
    assert add_element_to_active_tasks('     ', active_tasks) == ''
    assert add_element_to_active_tasks('a', active_tasks) == 'Already exists'
