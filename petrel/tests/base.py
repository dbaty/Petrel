import os

from pyramid import testing
from pyramid.url import resource_url

from webob.multidict import MultiDict
from webob.multidict import NestedMultiDict

from petrel.config import get_default_config
from petrel.views.utils import TemplateAPI


def get_fixture_path(filename):
    """Return the full path to the given ``filename`` in the fixtures
    directory.
    """
    return os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    

def setUp():
    """Set Pyramid registry and default Petrel configuration for our
    tests.
    """
    config = testing.setUp()
    global_config = {'here': 'dummy'}
    settings = {'auth_config_file': get_fixture_path('auth.ini')}
    get_default_config(global_config, config, **settings)
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
