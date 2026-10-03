from rest_framework.views import exception_handler as drf_handler


def exception_handler(exc, context):
    """Xatolar bir xil shaklda: {"error": "<kod>", "detail": ...}. Ichki tafsilot oshkor qilinmaydi."""
    response = drf_handler(exc, context)
    if response is None:
        return None
    detail = response.data
    code = getattr(exc, "default_code", "error")
    if isinstance(detail, dict) and set(detail) == {"detail"}:
        detail = detail["detail"]
    if isinstance(detail, str):
        code, detail = str(detail), None
    response.data = {"error": code, "detail": detail}
    return response
