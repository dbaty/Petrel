"""Login/logout views."""

from urllib import quote_plus
from urllib import unquote_plus

from pyramid.httpexceptions import HTTPSeeOther

from petrel.auth import get_who_api
from petrel.views.utils import get_template_api


def login_form(request, error=None):
    api = get_template_api(request)
    next = request.GET.get('next') or \
        request.POST.get('next') or \
        quote_plus(request.environ.get('HTTP_REFERER', None) or \
                       api.request.application_url)
    login = request.POST.get('login', '')
    return {'api': api,
            'login': login,
            'next': next,
            'error': error}


def login(request):
    next = request.POST.get('next', '') or request.application_url
    who_api = get_who_api(request.environ)
    creds = {'login': request.POST['login'],
             'password': request.POST['password']}
    authenticated, headers = who_api.login(creds)
    if not authenticated:
        return login_form(request, error=u'Wrong user name or password.')
    return HTTPSeeOther(location=unquote_plus(next), headers=headers)


def logout(request):
    who_api = get_who_api(request.environ)
    headers = who_api.logout()
    return HTTPSeeOther(location=request.application_url, headers=headers)


def forbidden(request): # FIXME: plug it
    # Called when a view raises Forbidden.
    location = '%s/login?next=%s' % (
        request.application_url,
        quote_plus(request.url))
    return HTTPSeeOther(location=location)
