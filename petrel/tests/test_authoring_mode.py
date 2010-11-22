"""Test ``AuthoringModeMiddleware``.

$Id$
"""

from unittest import TestCase


class TestAuthoringMode(TestCase):

    def _make_one(self, *args, **kwargs):
        from petrel.authoringmode import make_middleware
        return make_middleware(*args, **kwargs)

    def _call_fut(self, environ, *mw_args, **mw_kwargs):
        class FakeApp(object):
            def __call__(self, environ, start_response):
                return environ
        app = FakeApp()
        mw = self._make_one(app=app, global_conf=None,
                            *mw_args, **mw_kwargs)
        return mw(environ, start_response=None)

    def test_middleware_authoring_mode(self):
        environ = {'PATH_INFO': '/authoring/foo/bar'}
        got = self._call_fut(environ)
        self.assertEqual(got['PATH_INFO'], '/foo/bar')
        self.assertEqual(got['authoring_mode'], 'authoring')

    def test_middleware_not_in_authoring_mode(self):
        environ = {'PATH_INFO': '/foo/bar'}
        got = self._call_fut(environ.copy())
        self.assertEqual(got, environ)

    def test_custom_environ_key(self):
        environ = {'PATH_INFO': '/authoring/foo/bar'}
        got = self._call_fut(environ, environ_key='management_mode')
        self.assertEqual(got['PATH_INFO'], '/foo/bar')
        self.assertEqual(got['management_mode'], 'authoring')

    def test_custom_prefix(self):
        environ = {'PATH_INFO': '/manage/foo/bar'}
        got = self._call_fut(environ, prefix='manage')
        self.assertEqual(got['PATH_INFO'], '/foo/bar')
        self.assertEqual(got['authoring_mode'], 'manage')

    def test_path_starts_with_prefix_but_not_prefix(self):
        environ = {'PATH_INFO': '/authoring-foo/bar'}
        got = self._call_fut(environ.copy())
        self.assertEqual(got, environ)
