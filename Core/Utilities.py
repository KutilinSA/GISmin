import os
import io
import base64
import numpy as np
import struct
import zlib
import json
from urllib.parse import urlparse, uses_netloc, uses_params, uses_relative


_VALID_URLS = set(uses_relative + uses_netloc + uses_params)
_VALID_URLS.discard('')


def _is_url(url):
    """Check to see if `url` has a valid protocol."""
    try:
        return urlparse(url).scheme in _VALID_URLS
    except Exception:
        return False


def write_png(data, origin='upper', colormap=None):
    if colormap is None:
        def colormap(x):
            return x, x, x, 1

    arr = np.atleast_3d(data)
    height, width, nblayers = arr.shape

    if nblayers not in [1, 3, 4]:
        raise ValueError('Data must be NxM (mono), '
                         'NxMx3 (RGB), or NxMx4 (RGBA)')
    assert arr.shape == (height, width, nblayers)

    if nblayers == 1:
        arr = np.array(list(map(colormap, arr.ravel())))
        nblayers = arr.shape[1]
        if nblayers not in [3, 4]:
            raise ValueError('colormap must provide colors of r'
                             'length 3 (RGB) or 4 (RGBA)')
        arr = arr.reshape((height, width, nblayers))
    assert arr.shape == (height, width, nblayers)

    if nblayers == 3:
        arr = np.concatenate((arr, np.ones((height, width, 1))), axis=2)
        nblayers = 4
    assert arr.shape == (height, width, nblayers)
    assert nblayers == 4

    if arr.dtype != 'uint8':
        with np.errstate(divide='ignore', invalid='ignore'):
            arr = arr * 255./arr.max(axis=(0, 1)).reshape((1, 1, 4))
            arr[~np.isfinite(arr)] = 0
        arr = arr.astype('uint8')

    if origin == 'lower':
        arr = arr[::-1, :, :]

    raw_data = b''.join([b'\x00' + arr[i, :, :].tobytes()
                         for i in range(height)])

    def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return (struct.pack('!I', len(data)) +
                chunk_head +
                struct.pack('!I', 0xFFFFFFFF & zlib.crc32(chunk_head)))

    return b''.join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')])


def image_to_data(path, colormap=None, origin='upper'):
    if isinstance(path, str) and not _is_url(path):
        file_format = os.path.splitext(path)[-1][1:]
        with io.open(path, 'rb') as f:
            img = f.read()
        b64encoded = base64.b64encode(img).decode('utf-8')
        url = 'data:image/{};base64,{}'.format(file_format, b64encoded)
    elif 'ndarray' in path.__class__.__name__:
        img = write_png(path, origin=origin, colormap=colormap)
        b64encoded = base64.b64encode(img).decode('utf-8')
        url = 'data:image/png;base64,{}'.format(b64encoded)
    else:
        url = json.loads(json.dumps(path))
    return url.replace('\n', ' ')


def split_data_to_blocks(data, block_length):
    blocks = []
    tmp_block = ""
    for i in range(0, len(data)):
        tmp_block += data[i]
        if (i + 1) % block_length == 0:
            blocks.append(tmp_block)
            tmp_block = ""
        print(len(data) - i)
    if len(tmp_block) > 0:
        blocks.append(tmp_block)
    #while len(data) > 0:
    #    blocks.append(data[0:block_length])
    #    data = data[block_length:]
    #    print(len(data))
    return blocks
