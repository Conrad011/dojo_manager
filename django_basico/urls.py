from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
    path('alunos/', include('alunos.urls')),
    path('turmas/', include('turmas.urls')),
    path('presencas/', include('presencas.urls')),
    path('financeiro/', include('financeiro.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
