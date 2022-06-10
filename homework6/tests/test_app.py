from http import HTTPStatus
from typing import Iterator
from unittest import mock

import pytest
from fakeredis import FakeRedis  # type: ignore
from fastapi.testclient import TestClient
from PIL import Image
from rq import Queue

from app.app import add_task, app, get_queue, get_redis_client
from app.schemas import ResultImage, Statuses

TASK_ID = '3971b1df-0245-4e16-858b-46439dfc2792'
FAKE_TASK_ID = '3971b1df-0245-4e16-858b-46439dfc2793'


def fake_process(image_base64: str):
    image_data = image_base64.encode()
    return ResultImage(
        original=image_data,
        x64=image_data,
        x32=image_data,
    )


@pytest.fixture(scope='session')
def fake_redis_client():
    return FakeRedis()


@pytest.fixture(scope='session')
def fake_queue(fake_redis_client) -> Queue:
    return Queue(connection=fake_redis_client, is_async=False)


@pytest.fixture()
def fake_task(fake_queue: Queue, image_base64: str):
    return fake_queue.enqueue(fake_process, image_base64)


@pytest.fixture(scope='session')
def image():
    return Image.open('tests/images/сhevrolet_original.png')


@pytest.fixture(scope='session')
def client(fake_queue, fake_redis_client) -> TestClient:
    app.dependency_overrides[get_redis_client] = lambda: fake_redis_client
    app.dependency_overrides[get_queue] = lambda: fake_queue
    return TestClient(app)


@pytest.fixture(scope='session')
def image_file() -> Iterator[Image.Image]:
    with open('tests/images/сhevrolet_original.png', 'rb') as file:
        yield file


@pytest.fixture(scope='session')
def image_base64():
    with open('tests/images/chevrolet_original.txt', 'r', encoding='utf-8') as file:
        return file.read()


@pytest.fixture(scope='session')
def image32_base64():
    with open('tests/images/chevrolet_x32.txt', 'r', encoding='utf-8') as file:
        return file.read()


@pytest.fixture(scope='session')
def image64_base64():
    with open('tests/images/chevrolet_x64.txt', 'r', encoding='utf-8') as file:
        return file.read()


def test_get_task(fake_task, client: TestClient):
    response = client.get(f'/tasks/{fake_task.id}')
    assert response.status_code == HTTPStatus.OK
    fake_id = TASK_ID
    if fake_task.id == fake_id:
        fake_id = '3971b1df-0245-4e16-858b-46439dfc2793'
    response = client.get(f'/tasks/{fake_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND


@mock.patch('app.app.add_task')
def test_post_image(patch, client, image_file):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = TASK_ID
    response = client.post('/tasks', files={'image': image_file})
    assert response.status_code == HTTPStatus.OK


@mock.patch('app.app.add_task')
def test_add_task(patch, fake_queue, image_file):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = TASK_ID
    job = add_task(image_file, fake_queue)
    assert Statuses.from_rq(job.get_status()) == Statuses.DONE


# @pytest.mark.parametrize("request_path", [(f'/tasks/{TASK_ID}/image?size=32'),
#                                           (f'/tasks/{TASK_ID}/image?size=64'),
#                                           (f'/tasks/{TASK_ID}/image?size=original')])
@mock.patch('app.app.add_task')
def test_get_original_image_success(patch, fake_queue, image_file, client):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = TASK_ID
    job = add_task(image_file, fake_queue)
    response = client.get(f'/tasks/{job.id}/image?size=original')
    assert response.status_code == HTTPStatus.OK


@mock.patch('app.app.add_task')
def test_get_x32_image_success(patch, fake_queue, image_file, client):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = TASK_ID
    job = add_task(image_file, fake_queue)
    response = client.get(f'/tasks/{job.id}/image?size=32')
    assert response.status_code == HTTPStatus.OK


@mock.patch('app.app.add_task')
def test_get_x64_image_success(patch, fake_queue, image_file, client):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = TASK_ID
    job = add_task(image_file, fake_queue)
    response = client.get(f'/tasks/{job.id}/image?size=64')
    assert response.status_code == HTTPStatus.OK


@mock.patch('app.app.add_task')
def test_get_image_fail(patch, fake_queue, image_file, client):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = TASK_ID
    add_task(image_file, fake_queue)
    fake_id = FAKE_TASK_ID
    response = client.get(f'/tasks/{fake_id}/image?size=32')
    assert response.status_code == HTTPStatus.NOT_FOUND
