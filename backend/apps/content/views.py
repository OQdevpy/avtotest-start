import mimetypes

from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from binproto.crypto import CONTENT_TYPE, FLAG_RAW, pack_media, seal

from .models import Category, Question, Stage, Variant
from .serializers import media_path, tri


class CatalogView(APIView):
    """Bosh menyu uchun hamma ro'yxatlar bitta .bin faylda."""

    def get(self, request):
        published = Q(questions__is_published=True)
        categories = Category.objects.annotate(qcount=Count("questions", filter=published))
        stages = []
        for stage in Stage.objects.all():
            stages.append({
                "id": stage.id,
                "number": stage.number,
                "title": tri(stage, "title"),
                "categories": [
                    {"id": c.id, "title": tri(c, "title"), "count": c.qcount,
                     "icon": media_path("category", c, "icon")}
                    for c in categories if c.stage_id == stage.id
                ],
                "variants": [{"id": v.id, "number": v.number} for v in stage.variants.all()],
            })
        general = [{"id": v.id, "number": v.number} for v in Variant.objects.filter(stage__isnull=True)]
        return Response({"stages": stages, "variants": general})


class CategoryInfoView(APIView):
    def get(self, request, pk):
        c = get_object_or_404(Category, pk=pk)
        return Response({
            "id": c.id, "title": tri(c, "title"), "info": tri(c, "info"),
            "info_image": media_path("category", c, "info_image"),
        })


MEDIA_FIELDS = {
    "category": (Category.objects.all(), {"icon", "info_image"}),
    "question": (Question.objects.filter(is_published=True), {"image", "photo_hint", "audio_hint"}),
}


class MediaView(APIView):
    """Rasm/audio faqat shifrlangan .bin sifatida beriladi; to'g'ridan-to'g'ri
    /media/ URL umuman yo'q."""

    def get(self, request, kind, pk, field):
        if kind not in MEDIA_FIELDS or field not in MEDIA_FIELDS[kind][1]:
            raise Http404
        obj = get_object_or_404(MEDIA_FIELDS[kind][0], pk=pk)
        f = getattr(obj, field)
        if not f:
            raise Http404
        with f.open("rb") as fh:
            data = fh.read()
        mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        blob = seal(request.auth.key, pack_media(mime, data), path=request.path, direction="res", flags=FLAG_RAW)
        resp = HttpResponse(blob, content_type=CONTENT_TYPE)
        resp["Cache-Control"] = "no-store"
        return resp


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health(request):
    return Response({"ok": True})
