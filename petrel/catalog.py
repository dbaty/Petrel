"""Helpers for ``repoze.catalog`` integration.

$Id$
"""

from repoze.bfg.traversal import find_root
from repoze.bfg.traversal import model_path

from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap
from repoze.catalog.indexes.text import CatalogTextIndex


CATALOG_ID = '_catalog'
CATALOG_DOC_MAP_ID = '_catalog_doc_map'


def create_catalog_tools(site):
    setattr(site, CATALOG_ID, Catalog())
    setattr(site, CATALOG_DOC_MAP_ID, DocumentMap())
    catalog = getattr(site, CATALOG_ID)
    catalog['searchable_text'] = CatalogTextIndex(get_searchable_text)

def get_catalog_document_map(obj):
    site = find_root(obj)
    return getattr(site, CATALOG_DOC_MAP_ID)

def get_catalog(obj):
    site = find_root(obj)
    return getattr(site, CATALOG_ID)

def get_searchable_text(obj, _unused_default):
    return obj.get_searchable_text()

def get_all_contained_items_and_itself(self):
    """Return all contained items and itself."""
    if getattr(self, 'values', None):
        for item in self.values():
            get_all_contained_items_and_itself(item)
            yield item
    yield self

class CatalogAware:
    """A mixin class that defines catalog-related methods."""

    def _get_catalog_metadata(self):
        """Return metadata of this object that is going to be kept."""
        ## FIXME: shall we add other metadata?
        return dict(title=self.title,
                    path=model_path(self))

    def index(self):
        """Index object in the catalog."""
        doc_map = get_catalog_document_map(self)
        doc_id = doc_map.add(model_path(self))
        doc_map.add_metadata(doc_id, self._get_catalog_metadata())
        catalog = get_catalog(self)
        catalog.index_doc(doc_id, self)

    def reindex(self):
        """Reindex object in the catalog."""
        doc_map = get_catalog_document_map(self)
        doc_id = doc_map.docid_for_address(model_path(self))
        catalog = get_catalog(self)
        catalog.reindex_doc(doc_id, self)

    def unindex(self):
        """Remove references to this object from the catalog and
        propagate to contained items as well.
        """
        for item in get_all_contained_items_and_itself(self):
            doc_map = get_catalog_document_map(item)
            doc_id = doc_map.docid_for_address(model_path(item))
            doc_map.remove_docid(doc_id)
            catalog = get_catalog(item)
            catalog.unindex_doc(doc_id)


def index(event):
    event.object.index()

def reindex(event):
    event.object.reindex()

def unindex(event):
    event.object.unindex()
