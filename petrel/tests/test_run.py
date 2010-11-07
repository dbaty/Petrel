"""Test the ``run`` module.

$Id$
"""

from unittest import TestCase


class TestApp(TestCase):

    def test_app(self):
        ## This test looks dull but it actually checks that we have no
        ## error in the 'cofigure.zcml'.
        from tempfile import gettempdir
        from pyramid.router import Router
        from petrel.run import app
        global_settings = {}
        settings = {'zodb_uri': 'file://%s/Data.fs' % gettempdir()}
        wsgi_app = app(global_settings, **settings)
        self.assert_(isinstance(wsgi_app, Router))
