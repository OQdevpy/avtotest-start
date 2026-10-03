import json

from rest_framework.renderers import BaseRenderer

from .crypto import CONTENT_TYPE, FLAG_JSON, seal


def session_key(request):
    session = getattr(request, "auth", None) if request is not None else None
    return getattr(session, "key", None)


class BinRenderer(BaseRenderer):
    """Autentifikatsiyalangan javob → shifrlangan .bin. Kalit bo'lmasa (login,
    401) — oddiy JSON, chunki mijozda hali ochish uchun kalit yo'q."""

    media_type = CONTENT_TYPE
    format = "bin"
    charset = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        ctx = renderer_context or {}
        request, response = ctx.get("request"), ctx.get("response")
        key = session_key(request)
        if key is None:
            if response is not None:
                response["Content-Type"] = "application/json"
            return json.dumps(data, ensure_ascii=False).encode() if data is not None else b""
        if response is not None:
            response["Cache-Control"] = "no-store"
        return seal(key, data, path=request._request.path, direction="res", flags=FLAG_JSON)
