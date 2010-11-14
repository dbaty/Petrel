"""Test ``content.site.Site``.

$Id$
"""

from unittest import TestCase


class TestSite(TestCase):

    def setUp(self):
        from pyramid.configuration import Configurator
        self.config = Configurator()
        ## We need to register these templates since they are used in
        ## TemplateAPI which is in turn used in almost all views.
        self.config.testing_add_template('templates/layout.pt')
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _make_site(self):
        from petrel.content.site import Site
        return Site()

    def test_init(self):
        site = self._make_site()
        self.assert_(site.title, u'Site')

    def test_search_form(self):
        from petrel.content.site import search_form
        from pyramid.testing import DummyRequest
        req = DummyRequest()
        req.context = self._make_site()
        got = search_form(req)
        self.assert_(got['results'] is None)

    def test_search(self):
        pass ## FIXME
