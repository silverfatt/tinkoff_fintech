from enum import Enum

from pydantic import BaseModel


class Statuses(Enum):
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    FAILED = 'FAILED'

    @classmethod
    def from_rq(cls, data: str) -> 'Statuses':
        mapping = {
            'failed': cls.FAILED,
            'stopped': cls.FAILED,
            'finished': cls.DONE,
            'started': cls.IN_PROGRESS,
            'queued': cls.WAITING,
            'deferred': cls.WAITING,
        }
        return mapping[data.lower()]


class SizeOfImage(Enum):
    x32 = '32'
    x64 = '64'
    original = 'original'


class ResultImage(BaseModel):
    x32: bytes
    x64: bytes
    original: bytes
