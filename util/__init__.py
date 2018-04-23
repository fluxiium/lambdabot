import traceback
from django.utils import timezone


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
}


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
