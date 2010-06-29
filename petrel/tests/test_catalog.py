import unittest

from repoze.bfg.configuration import Configurator

from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap

from petrel.catalog import get_catalog
from petrel.catalog import get_catalog_document_map
from petrel.content.document import Document
from petrel.content.folder import Folder
from petrel.content.site import Site


class TestCatalog(unittest.TestCase):

    def setUp(self):
        self.config = Configurator()
        self.config.begin()
        self.config.load_zcml('petrel:configure.zcml')
        self.site = Site()

    def tearDown(self):
        self.config.end()

    def _makeDoc(self, parent=None):
        doc = Document()
        doc.title = u'Foo'
        doc.description = u'bar'
        doc.body = u'baz'
        if parent is None:
            parent = self.site
        parent.add('doc', doc)
        return doc

    def _makeFolder(self, parent=None):
        folder = Folder()
        folder.title = u'Folder'
        if parent is None:
            parent = self.site
        parent.add('folder', folder)
        return folder

    def _doSearch(self, **criteria):
        return self.site._catalog.search(**criteria)

    def test_get_catalog(self):
        doc_map = get_catalog(self.site)
        self.assert_(doc_map, Catalog)

    def test_get_catalog_doc_map(self):
        doc_map = get_catalog_document_map(self.site)
        self.assert_(doc_map, DocumentMap)

    def test_index(self):
        self._makeDoc()
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 1)

    def test_reindex(self):
        doc = self._makeDoc()
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 1)
        doc.edit(title=u'blah')
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 0)

    def test_unindex(self):
        doc = self._makeDoc()
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 1)
        self.site.remove(doc.__name__)
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 0)

    def test_unindex_when_container_is_removed(self):
        folder = self._makeFolder()
        self._makeDoc(folder)
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 1)
        self.site.remove(folder.__name__)
        res = self._doSearch(searchable_text='foo')
        self.assertEqual(res[0], 0)
