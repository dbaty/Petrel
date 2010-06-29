"""Define the ``Site`` (so-called) content type and everything related
to it: forms, views, etc.

$Id$
"""

from zope.interface import implements

from petrel.catalog import create_catalog_tools
from petrel.catalog import get_catalog
from petrel.catalog import get_catalog_document_map
from petrel.content.folder import Folder
from petrel.interfaces import IFolderish
from petrel.views import get_default_view_bindings


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Site()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']


class Site(Folder):
    implements(IFolderish)

    __parent__ = __name__ = None

    def __init__(self):
        Folder.__init__(self)
        create_catalog_tools(self)
        self.title = u'Site'
        self.description = u'A site.'

def search_form(request):
    bindings = get_default_view_bindings(request)
    bindings.update(results=None)
    return bindings


def search(request):
    bindings = get_default_view_bindings(request)
    catalog = get_catalog(request.context)
    results = catalog.search(
        searchable_text=request.POST.get('text', ''),
        sort_index='searchable_text')
    results = results[1] ## results[0] is the number of results
    doc_map = get_catalog_document_map(request.context)
    results = [doc_map.get_metadata(doc_id) for doc_id in results]
    bindings.update(results=results)
    return bindings


def debug(request): ## FIXME: debug only
    context = request.context
    from repoze.bfg.traversal import find_root
    site = find_root(context)
    import pdb; pdb.set_trace()
    site
