"""Test ``content.folder.Folder``.

$Id$
"""

from unittest import TestCase

from pyramid import testing


class TestFolder(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from petrel.config import set_default_config
        set_default_config(self.config)

    def tearDown(self):
        testing.tearDown()

    def _make_site(self):
        from petrel.content.site import Site
        return Site()

    def _make_folder(self, parent, name):
        from petrel.content.folder import Folder
        folder = Folder()
        folder.id = name ## FIXME: is this needed?
        parent.add(name, folder)
        return folder

    def _make_document(self, parent, name):
        from petrel.content.document import Document
        document = Document()
        document.id = name ## FIXME: is this needed?
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

    def test_validate_id(self):
        from petrel.content.folder import FORBIDDEN_NAMES
        folder = self._make_folder(self._make_site(), 'folder')
        self._make_document(folder, 'doc1')
        allowed = ('doc2', 'foo', 'foo_bar', 'foo-bar.baz')
        forbidden = ('_foo', '-foo', '.foo', 'a/b', 'a?', u'\xe9', 'doc1')
        forbidden += FORBIDDEN_NAMES
        for name in allowed:
            self.assert_(folder.validate_id(name),
                         '%s should be allowed' % name)
        for name in forbidden:
            self.assert_(not folder.validate_id(name),
                         '%s should be forbidden' % name)

    def test_delete(self):
        from pyramid.url import model_url
        from petrel.content.folder import folder_delete
        folder = self._make_folder(self._make_site(), 'folder')
        self._make_document(folder, 'doc1')
        self._make_document(folder, 'doc2')
        self._make_document(folder, 'doc3')
        post = (('selected', 'doc1'), ('selected', 'doc2'))
        req = self._make_request(context=folder, post=post)
        resp = folder_delete(req)
        self.assert_(resp.headers['Location'], model_url(folder, req))
        self.assertEqual(list(folder.keys()), ['doc3'])

    def test_rename_form(self):
        from petrel.content.folder import folder_rename_form
        folder = self._make_folder(self._make_site(), 'folder')
        doc1 = self._make_document(folder, 'doc1')
        doc1.title = u'Document 1'
        doc2 = self._make_document(folder, 'doc2')
        doc2.title = u'Document 2'
        post = (('selected', 'doc1'), ('selected', 'doc2'))
        req = self._make_request(context=folder, post=post)
        bindings = folder_rename_form(req)
        self.assertEqual(bindings['items'],
                         [{'id': 'doc1',
                           'title': 'Document 1'},
                          {'id': 'doc2',
                           'title': 'Document 2'}])

    def test_rename_item(self):
        from pyramid.url import model_url
        from petrel.content.folder import folder_rename
        site = self._make_site()
        folder = self._make_folder(site, u'folder')
        subfolder = self._make_folder(folder, u'subfolder')
        self._make_document(subfolder, u'doc1')
        self._make_document(subfolder, u'doc2')
        req = self._make_request(context=folder,
                                 post={'name_orig': u'subfolder',
                                       'name_new': u'the-subfolder'})
        resp = folder_rename(req)
        self.assertEqual(resp.status, '302 Found')
        self.assert_(resp.headers['Location'], model_url(folder, req))
        self.assertEqual(list(folder.keys()), [u'the-subfolder'])
        self.assertEqual(subfolder.__name__, u'the-subfolder')

        ## Check that the subfolder and its sub-items have been
        ## reindexed.
        from petrel.catalog import get_catalog
        from petrel.catalog import get_catalog_document_map
        catalog = get_catalog(site)
        res = catalog.search(path='/folder/subfolder')
        self.assertEqual(res[0], 0)
        res = catalog.search(path='/folder/the-subfolder')
        doc_map = get_catalog_document_map(site)
        res = [doc_map.get_metadata(doc_id)['path'] for doc_id in res[1]]
        self.assertEqual(res, ['/folder/the-subfolder/doc1',
                               '/folder/the-subfolder/doc2'])
