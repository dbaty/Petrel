"""Define utility for views.

FIXME: should we rename this module?

$Id$
"""

from urllib import quote_plus

from webob.exc import HTTPFound

from petrel.utils import TemplateAPI


def get_default_view_bindings(request):
    context = request.context
    api = TemplateAPI(request)
    addable_types = context.get_addable_types(request.registry)
    return dict(api=api,
                load_jquery=False,
                load_editor=False,
                addable_types=addable_types,
                request=request,
                context=context,
                context_url=context.get_url(request))

def redirect_to(url, **kwargs):
    """Redirect to ``url`` with the given arguments as GET parameters.
    """
    if kwargs:
        url += '?'
        for param, value in kwargs.items():
            url += u'%s=%s&' % (param, quote_plus(value))
        url = url.rstrip('&')
    return HTTPFound(location=url)
