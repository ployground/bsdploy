import hashlib
import os
import sys
import urllib


def check(path, sha):
    d = hashlib.sha1()
    with open(path, 'rb') as f:
        while 1:
            buf = f.read(1024 * 1024)
            if not len(buf):
                break
            d.update(buf)
    return d.hexdigest() == sha


def run(*args, **kwargs):
    url = sys.argv[1]
    sha = sys.argv[2]
    path = sys.argv[3]
    if os.path.isdir(path):
        import urlparse
        path = os.path.join(path, urlparse.urlparse(url).path.split('/')[-1])
    if os.path.exists(path):
        if not check(path, sha):
            os.remove(path)
    if not os.path.exists(path):
        urllib.urlretrieve(url, path)
        if not check(path, sha):
            sys.exit(1)


if __name__ == '__main__':
    run()
