"""Define the ``Site`` class."""

from petrel.search import create_catalog_tools
from petrel.content.folder import Folder


class Site(Folder):
    """A site is the top-level object that holds, well, all contents
    of the web site.
    """

    __parent__ = __name__ = None

    def __init__(self):
        Folder.__init__(self)
        create_catalog_tools(self)
        self.title = u'Site'
        self.description = u'A site.'
        self.index() # for 'utils.get_nav_tree()' to work properly ## FIXME: really?
