import hashlib

READ_BUFFER_SIZE = 2**20


def md5_for_path(path, block_size=READ_BUFFER_SIZE):
    with open(path, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()
