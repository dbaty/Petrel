"""Define utility for views.

FIXME: should we rename this module?

$Id$
"""

from petrel.utils import TemplateAPI


def get_default_view_bindings(request): ## FIXME: useless
    context = request.context
    api = TemplateAPI(request)
    return dict(api=api, context=context)


def toolbar(request):
    from petrel.content.base import get_template_api ## FIXME: move outside
    return {
        'api': get_template_api(request),
        }
