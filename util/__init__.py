import traceback
import uuid
from urllib.parse import urlparse
from django.utils import timezone


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
}


def struuid4():
    return str(uuid.uuid4())


# noinspection PyBroadException
def is_url(x):
    try:
        result = urlparse(x)
        return bool(result.scheme and result.netloc and result.path)
    except Exception:
        return False


def log(*args, tag=None):
    if tag is not None:
        tag = "[{}]".format(tag)
    else:
        tag = ""
    print(timezone.now(), tag, *args)


def log_exc(exc: Exception):
    log("--- ERROR ---")
    print(exc)
    tb = traceback.format_exception(None, exc, exc.__traceback__)
    tb_str = ""
    for line in tb:
        tb_str += line
    tb_str = tb_str.strip().replace("\n\n", "\n")
    print(tb_str)
