from unittest import TestCase


class TestCatalog(TestCase):

    def setUp(self):
        from petrel.content.site import Site
        from petrel.tests.base import setUp
        self.config = setUp()
        self.site = Site()

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()

    def _make_document(self, parent=None):
        from petrel.content.document import Document
        doc = Document()
        doc.title = u'Foo'
        doc.description = u'bar'
        doc.body = u'baz'
        if parent is None:
            parent = self.site
        parent.add(self.config.registry, 'doc', doc)
        return doc

    def _make_folder(self, parent=None):
        from petrel.content.folder import Folder
        folder = Folder()
        folder.title = u'Folder'
        if parent is None:
            parent = self.site
        parent.add(self.config.registry, 'folder', folder)
        return folder

    def _do_search(self, **criteria):
        return self.site._catalog.search(**criteria)

    def test_get_catalog(self):
        from repoze.catalog.catalog import Catalog
        from petrel.search import get_catalog
        doc_map = get_catalog(self.site)
        self.assert_(doc_map, Catalog)

    def test_get_catalog_doc_map(self):
        from repoze.catalog.document import DocumentMap
        from petrel.search import get_catalog_document_map
        doc_map = get_catalog_document_map(self.site)
        self.assert_(doc_map, DocumentMap)

    def test_index(self):
        self._make_document()
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 1)

    def test_reindex(self):
        doc = self._make_document()
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 1)
        doc.edit(title=u'blah')
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 0)

    def test_unindex(self):
        doc = self._make_document()
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 1)
        self.site.remove(self.config.registry, doc.__name__)
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 0)

    def test_unindex_when_container_is_removed(self):
        folder = self._make_folder()
        self._make_document(folder)
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 1)
        self.site.remove(self.config.registry, folder.__name__)
        res = self._do_search(searchable_text='foo')
        self.assertEqual(res[0], 0)


class TestSearch(TestCase):

    def setUp(self):
        from petrel.tests.base import setUp
        self.config = setUp()

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()

    def _call_fut(self, *args, **kwargs):
        from petrel.search import search
        return search(*args, **kwargs)

    def _make_site(self):
        from petrel.content.site import Site
        return Site()

    def _make_document(self, parent, name):
        from petrel.content.document import Document
        document = Document()
        document.id = name
        parent.add(self.config.registry, name, document)
        return document

    def test_search(self):
        site = self._make_site()
        doc = self._make_document(site, 'doc')
        doc.edit(title='Document')
        res = self._call_fut(context=site, searchable_text=u'document')
        self.assertEqual([r['path'] for r in res], ['/doc'])

    def test_search_empty_request(self):
        site = self._make_site()
        doc = self._make_document(site, 'doc')
        doc.edit(title='Document')
        res = self._call_fut(context=site, searchable_text=u'')
        self.assertEqual(res, ())
