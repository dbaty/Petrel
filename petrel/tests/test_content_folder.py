from unittest import TestCase


class TestFolder(TestCase):

    def setUp(self):
        from petrel.tests.base import setUp
        self.config = setUp()

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()

    def _make_site(self):
        from petrel.content.site import Site
        return Site()

    def _make_folder(self, parent, name):
        from petrel.content.folder import Folder
        folder = Folder()
        folder.id = name ## FIXME: is this needed?
        parent.add(self.config.registry, name, folder)
        return folder

    def _make_document(self, parent, name):
        from petrel.content.document import Document
        document = Document()
        document.id = name ## FIXME: is this needed?
        parent.add(self.config.registry, name, document)
        return document

    def _make_request(self, context, post=None):
        from petrel.tests.base import DummyRequest
        return DummyRequest(context, post=post)

    def test_validate_id(self):
        folder = self._make_folder(self._make_site(), 'folder')
        self._make_document(folder, 'doc1')
        allowed = ('doc2', 'foo', 'foo_bar', 'foo-bar.baz', 'edit')
        forbidden = ('_foo', '-foo', '.foo', '@foo', 'a/b',
                     'a?', u'\xe9', 'doc1')
        for name in allowed:
            self.assert_(folder.validate_id(name),
                         '%s should be allowed' % name)
        for name in forbidden:
            self.assert_(not folder.validate_id(name),
                         '%s should be forbidden' % name)

    def test_delete(self):
        from pyramid.url import resource_url
        from petrel.content.folder import folder_delete
        folder = self._make_folder(self._make_site(), 'folder')
        self._make_document(folder, 'doc1')
        self._make_document(folder, 'doc2')
        self._make_document(folder, 'doc3')
        post = (('selected', 'doc1'), ('selected', 'doc2'))
        req = self._make_request(context=folder, post=post)
        resp = folder_delete(req)
        self.assert_(resp.headers['Location'], resource_url(folder, req))
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
        from pyramid.url import resource_url
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
        self.assertEqual(resp.status, '303 See Other')
        self.assert_(resp.headers['Location'], resource_url(folder, req))
        self.assertEqual(list(folder.keys()), [u'the-subfolder'])
        self.assertEqual(subfolder.__name__, u'the-subfolder')

        ## Check that the subfolder and its sub-items have been
        ## reindexed.
        from petrel.search import search
        res = search(site, path='/folder/subfolder')
        self.assertEqual(res, ())
        res = search(site, path='/folder/the-subfolder')
        res = [i['path'] for i in res]
        self.assertEqual(res, ['/folder/the-subfolder/doc1',
                               '/folder/the-subfolder/doc2'])
