"""Define a WSGI middleware that tags the environment if ``PATH_INFO``
starts with a certain prefix (usually "/authoring/" or "/manage/")

It can be used by the main application to provide a different
behaviour or theme when viewing in this mode.

Note that the application is responsible of tweaking computed URLs so
that they may (or may not) include the prefix.

$Id$
"""


class AuthoringModeMiddleware(object):

    def __init__(self, app, prefix='authoring',
                 environ_key='authoring_mode'):
        """If ``PATH_INFO`` starts with the given prefix, add a key in
        the environment, remove the prefix from ``PATH_INFO`` and pass
        along to the application.
        """
        self.app = app
        self.prefix = prefix
        self.environ_key = environ_key

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/%s/' % self.prefix):
            environ[self.environ_key] = self.prefix
            environ['PATH_INFO'] = environ['PATH_INFO'][1 + len(self.prefix):]
        return self.app(environ, start_response)


def make_middleware(app, global_conf, **kwargs):
    return AuthoringModeMiddleware(app, **kwargs)
