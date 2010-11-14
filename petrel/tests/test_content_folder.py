"""Test ``content.folder.Folder``.

$Id$
"""

from unittest import TestCase


class TestFolder(TestCase):

    def setUp(self):
        from pyramid.configuration import Configurator
        self.config = Configurator()
        ## We need to register these templates since they are used in
        ## TemplateAPI which is in turn used in almost all views.
        self.config.testing_add_template('templates/layout.pt')
        self.config.begin()
        self.config.load_zcml('petrel:configure.zcml')

    def tearDown(self):
        self.config.end()

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
        document.id = name
        parent.add(name, document)
        return document

    def _make_request(self, post=None, context=None):
        from pyramid.testing import DummyRequest
        if post is not None:
            from webob.multidict import MultiDict
            post = MultiDict(post)
        req = DummyRequest(post=post)
        req.context = context
        return req

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
