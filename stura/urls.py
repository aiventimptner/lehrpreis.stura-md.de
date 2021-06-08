from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import path, include
from django.utils import translation


def set_language(request, code: str):
    if code not in dict(settings.LANGUAGES).keys():
        return HttpResponseBadRequest("This language code is not allowed. Possible choices are 'de' or 'en'.")
    translation.activate(code)
    target_url = f'/{code}' + request.GET.get('redirect_to', '/')
    response = HttpResponseRedirect(redirect_to=target_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, code)
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('lang/<str:code>/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('', include('award.urls')),
)
