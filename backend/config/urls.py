from django.conf import settings
from django.contrib import admin
from django.urls import path

from apps.accounts import views as acc
from apps.content import views as content
from apps.exams import views as exams

admin.site.site_header = "AvtoStart boshqaruv"

api = [
    path("health/", content.health),
    path("auth/login/", acc.LoginView.as_view()),
    path("auth/logout/", acc.LogoutView.as_view()),
    path("auth/me.bin", acc.MeView.as_view()),
    path("catalog.bin", content.CatalogView.as_view()),
    path("categories/<int:pk>/info.bin", content.CategoryInfoView.as_view()),
    path("media/<str:kind>/<int:pk>/<str:field>.bin", content.MediaView.as_view()),
    path("attempts/start.bin", exams.StartView.as_view()),
    path("attempts/history.bin", exams.HistoryView.as_view()),
    path("attempts/<int:pk>.bin", exams.AttemptView.as_view()),
    path("attempts/<int:pk>/answer.bin", exams.AnswerView.as_view()),
    path("attempts/<int:pk>/finish.bin", exams.FinishView.as_view()),
]

urlpatterns = [path(settings.ADMIN_URL, admin.site.urls)] + [path("api/" + str(p.pattern), p.callback) for p in api]
