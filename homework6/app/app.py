from io import BytesIO
from typing import IO, Any

import fastapi
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from PIL import Image
from pydantic import UUID4
from redis import Redis  # type: ignore
from rq import Queue
from rq.job import Job
from starlette.responses import StreamingResponse

from app.func import decode, encode, get_different_sizes
from app.schemas import SizeOfImage, Statuses

STATUS_OK = {'status': 'ok'}
ONE_HOUR = 60 * 60
app = FastAPI()


# host='redis', port=6379, decode_responses=True
def make_redis_client() -> 'Redis[Queue]':
    return Redis(host='redis', port=6379, decode_responses=False)


def get_redis_client() -> 'Redis[Queue]':
    return make_redis_client()


def make_queue() -> Queue:
    return Queue(connection=make_redis_client())


def get_queue() -> Queue:
    return make_queue()


def add_task(
    image_data: IO[bytes],
    image_processing_queue: Queue,
) -> Job:
    """
    Add task to queue
    """
    image = Image.open(image_data)
    job = image_processing_queue.enqueue(
        get_different_sizes, encode(image), result_ttl=ONE_HOUR
    )
    return job


@app.post('/tasks')
def post_image(
    image: UploadFile = File(...),
    queue: Queue = Depends(get_queue),
) -> Any:
    """
    Get image from user and add it to queue
    """
    job = add_task(image.file, queue)
    return {'id': job.id, 'status': Statuses.from_rq(job.get_status())}


@app.get('/tasks/{task_id}')
def get_task(
    task_id: UUID4,
    queue: Queue = Depends(get_queue),
) -> Any:
    """
    Check task status
    """
    job = queue.fetch_job(str(task_id))
    if job is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='TASK DOES NOT EXISTS',
        )
    status = job.get_status()
    return {'id': job.id, 'status': Statuses.from_rq(status)}


@app.get('/tasks/{task_id}/image')
def get_image(
    task_id: UUID4,
    size: SizeOfImage,
    queue: Queue = Depends(get_queue),
) -> StreamingResponse:
    """
    Add task to queue
    """
    job = queue.fetch_job(str(task_id))
    if job is None:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='TASK DOES NOT EXISTS',
        )
    if Statuses.from_rq(job.get_status()) != Statuses.DONE:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail='TASK IS NOT READY'
        )

    if size == SizeOfImage.original:
        image_data = job.result.original
    elif size == SizeOfImage.x64:
        image_data = job.result.x64
    else:
        image_data = job.result.x32

    image = decode(image_data)
    buffer = BytesIO()
    image.save(buffer, 'png')
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='image/png')
