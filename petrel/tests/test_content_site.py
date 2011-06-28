"""Test ``content.site.Site``.

$Id$
"""

from unittest import TestCase

from pyramid import testing


class TestSite(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from petrel.config import set_default_config
        set_default_config(self.config)

    def tearDown(self):
        testing.tearDown()

    def _make_site(self):
        from petrel.content.site import Site
        return Site()

    def _make_document(self, parent, name):
        from petrel.content.document import Document
        document = Document()
        document.id = name
        parent.add(name, document)
        return document

    def _make_request(self, context=None, post=None):
        from pyramid.testing import DummyRequest
        if post is not None:
            from webob.multidict import MultiDict
            post = MultiDict(post)
        req = DummyRequest(post=post)
        req.context = context
        return req

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
        from petrel.content.site import search
        site = self._make_site()
        doc = self._make_document(site, 'doc')
        doc.edit(title='Document')
        req = self._make_request(context=site,
                                 post={'text': u'document'})
        got = search(req)
        self.assertEqual(got['n_results'], 1)
        self.assertEqual([r['path'] for r in got['results']], ['/doc'])

    def test_search_empty_request(self):
        from petrel.content.site import search
        req = self._make_request(context=self._make_site(),
                                 post={'text': u''})
        got = search(req)
        self.assertEqual(got['n_results'], 0)
        self.assertEqual(got['results'], ())
