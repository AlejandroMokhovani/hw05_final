from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # регистрация и авторизация
    path('auth/', include('users.urls', namespace='users')),

    # если нужного шаблона для /auth не нашлось в файле users.urls —
    # ищем совпадения в файле django.contrib.auth.urls
    path('auth/', include('django.contrib.auth.urls')),

    # раздел администратора
    path('admin/', admin.site.urls),

    path('about/', include('about.urls', namespace='about')),
    # обработчик для главной страницы ищем в urls.py приложения posts
    path("", include('posts.urls')),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
