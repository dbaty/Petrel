from pyramid import testing
from pyramid.url import resource_url

from webob.multidict import MultiDict
from webob.multidict import NestedMultiDict

from petrel.config import get_default_config
from petrel.views.utils import TemplateAPI


def setUp():
    """Set Pyramid registry and default Petrel configuration for our
    tests.
    """
    config = testing.setUp()
    get_default_config({}, config)
    config.register_template_api(TemplateAPI)
    return config


class DummyRequest(testing.DummyRequest):
    """While Pyramid provides a dummy request class, it is sometimes a
    bit too simple. On the other hand, we usually do not want the
    regular ``pyramid.request.Request`` as it is not particularly easy
    to use.
    """

    def __init__(self, context, environ=None, get=None, post=None):
        if environ is None:
            environ = {}
        post = MultiDict(post or {})
        testing.DummyRequest.__init__(self, environ=environ, post=post)
        self.context = context
        self.GET = MultiDict(get or {})
        if get or post:
            ## That's what 'webob.Request.str_params()' does
            self.params = NestedMultiDict(self.GET, self.POST)

    def resource_url(self, resource, *elements, **kw):
        return resource_url(resource, self, *elements, **kw)
