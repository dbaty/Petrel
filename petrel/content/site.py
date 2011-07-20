"""Define the ``Site`` class as well as the "application maker".

$Id$
"""

from zope.interface import implements

from petrel.catalog import create_catalog_tools
from petrel.catalog import get_catalog
from petrel.catalog import get_catalog_document_map
from petrel.content.folder import Folder
from petrel.interfaces import IFolderish
from petrel.views import get_default_view_bindings


class Site(Folder):
    implements(IFolderish)

    __parent__ = __name__ = None

    def __init__(self):
        Folder.__init__(self)
        create_catalog_tools(self)
        self.title = u'Site'
        self.description = u'A site.'
        self.index() ## for 'utils.get_nav_tree()' to work properly



## FIXME: just provide a utility function to be called by a view in
## the application.
def search(request):
    bindings = get_default_view_bindings(request)
    text = request.POST.get('text', '')
    if text:
        catalog = get_catalog(request.context)
        results = catalog.search(searchable_text=text,
                                 sort_index='searchable_text')
        n_results, results = results
        if results:
            doc_map = get_catalog_document_map(request.context)
            results = [doc_map.get_metadata(doc_id) for doc_id in results]
    else:
        n_results = 0
        results = ()
    bindings.update(n_results=n_results, results=results)
    return bindings
