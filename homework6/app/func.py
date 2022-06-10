from base64 import b64decode, b64encode
from io import BytesIO

from PIL import Image

from app.schemas import ResultImage


def convert_image_to_bytes(image: Image.Image) -> bytes:
    """
    Convert image to byres
    """
    buffer = BytesIO()
    image.save(buffer, 'png')
    return buffer.getvalue()


def convert_bytes_to_image(data: bytes) -> Image.Image:
    """
    Convert bytes back to image
    """
    buffer = BytesIO(data)
    return Image.open(buffer)


def encode(image: Image.Image) -> bytes:
    """
    Encode image using base64
    """
    return b64encode(convert_image_to_bytes(image))


def decode(data: bytes) -> Image.Image:
    """
    Decode image encoded with base64
    """
    return convert_bytes_to_image(b64decode(data))


def get_different_sizes(data: bytes) -> ResultImage:
    """
    Get 3 versions of image: 64, 32 and original
    """
    image_original = decode(data)
    image_x64 = image_original.resize((64, 64))
    image_x32 = image_original.resize((32, 32))
    return ResultImage(
        x32=encode(image_x32),
        x64=encode(image_x64),
        original=encode(image_original),
    )
