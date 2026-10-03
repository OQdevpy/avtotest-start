import logging
import time

from django.conf import settings
from django.core.cache import cache
from rest_framework import exceptions
from rest_framework.parsers import BaseParser

from .crypto import CONTENT_TYPE, FLAG_JSON, BinError, open_
from .renderers import session_key

log = logging.getLogger("security")
MAX_BODY = 2 * 1024 * 1024


class BinParser(BaseParser):
    """Shifrlangan .bin so'rov tanasi.

    Ichki JSON'da `_ts` (ms) va `_n` (tasodifiy nonce) bo'lishi shart: eskirgan
    yoki ikkinchi marta yuborilgan so'rov (replay) rad etiladi.
    """

    media_type = CONTENT_TYPE

    def parse(self, stream, media_type=None, parser_context=None):
        request = parser_context["request"]
        key = session_key(request)
        if key is None:
            raise exceptions.NotAuthenticated()
        blob = stream.read(MAX_BODY + 1) if stream else b""
        if len(blob) > MAX_BODY:
            raise exceptions.ParseError("too_large")
        try:
            flags, data = open_(key, blob, path=request._request.path, direction="req")
        except BinError as exc:
            log.warning("bin open failed sid=%s path=%s: %s", request.auth.sid, request._request.path, exc)
            raise exceptions.ParseError("bad_bin")
        if flags != FLAG_JSON or not isinstance(data, dict):
            raise exceptions.ParseError("bad_bin")

        ts, nonce = data.pop("_ts", None), data.pop("_n", None)
        if not isinstance(ts, (int, float)) or not isinstance(nonce, str) or not 8 <= len(nonce) <= 64:
            raise exceptions.ParseError("bad_bin")
        if abs(time.time() - ts / 1000) > settings.BIN_MAX_CLOCK_SKEW:
            raise exceptions.ParseError("clock_skew")
        if not cache.add(f"bin-n:{request.auth.sid}:{nonce}", 1, settings.BIN_MAX_CLOCK_SKEW * 2):
            log.warning("bin replay sid=%s path=%s", request.auth.sid, request._request.path)
            raise exceptions.ParseError("replay")
        return data
