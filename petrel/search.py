from pyramid.traversal import find_root
from pyramid.traversal import resource_path

from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap
from repoze.catalog.indexes.path2 import CatalogPathIndex2
from repoze.catalog.indexes.text import CatalogTextIndex


CATALOG_ID = '_catalog'
CATALOG_DOC_MAP_ID = '_catalog_doc_map'


def get_catalog(obj):
    """Return the catalog."""
    site = find_root(obj)
    return getattr(site, CATALOG_ID)


def get_catalog_document_map(obj):
    """Return the document map."""
    site = find_root(obj)
    return getattr(site, CATALOG_DOC_MAP_ID)


def create_catalog_tools(site):
    """Create catalog-related tools."""
    catalog = Catalog()
    catalog['path'] = CatalogPathIndex2(_get_path)
    catalog['searchable_text'] = CatalogTextIndex(_get_searchable_text)
    setattr(site, CATALOG_ID, catalog)
    setattr(site, CATALOG_DOC_MAP_ID, DocumentMap())


def _get_path(obj, _unused_default=None):
    return resource_path(obj)


def _get_searchable_text(obj, _unused_default):
    return obj.get_searchable_text()


def _get_all_contained_items_and_itself(obj):
    yield obj
    if getattr(obj, 'values', None):
        for item in obj.values():
            for i in _get_all_contained_items_and_itself(item):
                yield i


def search(context, sort_index=None, **criteria):
    """Return a list of metadata for the matching items."""
    if not any(criteria.values()):
        return ()
    catalog = get_catalog(context)
    results = catalog.search(sort_index=sort_index, **criteria)
    n_results, results = results
    if not results:
        return ()
    doc_map = get_catalog_document_map(context)
    return [doc_map.get_metadata(doc_id) for doc_id in results]


class CatalogAware:
    """A mixin class that defines catalog-related methods."""

    def _get_catalog_metadata(self):
        """Return metadata of this object that is going to be kept."""
        return dict(title=self.title,
                    path=resource_path(self))

    def index(self):
        """Index object in the catalog."""
        for item in _get_all_contained_items_and_itself(self):
            doc_map = get_catalog_document_map(item)
            doc_id = doc_map.add(resource_path(item))
            doc_map.add_metadata(doc_id, item._get_catalog_metadata())
            catalog = get_catalog(item)
            catalog.index_doc(doc_id, item)

    def reindex(self):
        """Reindex object in the catalog."""
        ## FIXME: would be nice to be able to reindex only specific
        ## indexes. This would need to be implemented in
        ## 'repoze.catalog' first.
        for item in _get_all_contained_items_and_itself(self):
            doc_map = get_catalog_document_map(item)
            doc_id = doc_map.docid_for_address(resource_path(item))
            doc_map.add_metadata(doc_id, item._get_catalog_metadata())
            catalog = get_catalog(item)
            catalog.reindex_doc(doc_id, item)

    def unindex(self):
        """Remove references to this object from the catalog and
        propagate to contained items as well.
        """
        for item in _get_all_contained_items_and_itself(self):
            doc_map = get_catalog_document_map(item)
            doc_id = doc_map.docid_for_address(resource_path(item))
            doc_map.remove_docid(doc_id)
            catalog = get_catalog(item)
            catalog.unindex_doc(doc_id)


def index(event):
    event.object.index()


def reindex(event):
    event.object.reindex()


def unindex(event):
    event.object.unindex()
