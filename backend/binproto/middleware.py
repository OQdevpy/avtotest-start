from django.conf import settings

CSP = (
    "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
)


class SecurityHeadersMiddleware:
    """API javoblariga qat'iy sarlavhalar. Admin sahifalariga CSP qo'yilmaydi
    (Django admin inline skriptlardan foydalanadi)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            response.setdefault("Content-Security-Policy", CSP)
            response.setdefault("Cache-Control", "no-store")
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        return response


class CorsMiddleware:
    """Faqat CORS_ALLOWED_ORIGINS ro'yxatidagi manbalarga ruxsat. Odatda frontend
    va API bitta domenda (nginx orqali) — u holda ro'yxat bo'sh qoladi."""

    ALLOW_HEADERS = "Authorization, Content-Type, X-Device-Id"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        allowed = origin and origin in settings.CORS_ALLOWED_ORIGINS and request.path.startswith("/api/")
        if allowed and request.method == "OPTIONS":
            from django.http import HttpResponse
            response = HttpResponse(status=204)
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = self.ALLOW_HEADERS
            response["Access-Control-Max-Age"] = "600"
        else:
            response = self.get_response(request)
        if allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
        return response
