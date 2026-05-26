from django.contrib import admin
from django.urls import path
from ingestion.views import (
    LoginView, LogoutView, MeView,
    ClientListView, IngestFileView, BatchListView,
    EmissionRecordListView, EmissionRecordDetailView,
    ApproveRecordView, RejectRecordView,
    DashboardStatsView, AuditLogView,
)

from django.http import HttpResponse
from django.contrib import admin
from django.urls import path

def home(request):
    return HttpResponse("Breathe ESG Backend is live 🚀")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
]

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/logout/', LogoutView.as_view()),
    path('api/auth/me/', MeView.as_view()),

    # Clients
    path('api/clients/', ClientListView.as_view()),

    # Ingestion
    path('api/ingest/', IngestFileView.as_view()),
    path('api/batches/', BatchListView.as_view()),

    # Review
    path('api/emissions/', EmissionRecordListView.as_view()),
    path('api/emissions/<int:pk>/', EmissionRecordDetailView.as_view()),
    path('api/emissions/<int:pk>/approve/', ApproveRecordView.as_view()),
    path('api/emissions/<int:pk>/reject/', RejectRecordView.as_view()),
    path('api/emissions/<int:pk>/audit/', AuditLogView.as_view()),

    # Dashboard
    path('api/dashboard/', DashboardStatsView.as_view()),
]