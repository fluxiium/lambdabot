import traceback
import uuid
import logging
from urllib.parse import urlparse

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


def log_exc(exc: Exception, ctx=None):
    errstr = "--- ERROR ---\n"
    if ctx:
        errstr += f'{ctx.guild}, #{ctx.channel}, {ctx.author}: {ctx.message.content}\n'
    errstr += str(exc) + '\n'
    tb = traceback.format_exception(None, exc, exc.__traceback__)
    tb_str = ""
    for line in tb:
        tb_str += line
    tb_str = tb_str.strip().replace("\n\n", "\n")
    errstr += tb_str
    logging.debug(errstr)
