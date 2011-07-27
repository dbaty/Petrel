from petrel.search import create_catalog_tools
from petrel.content.folder import Folder


class Site(Folder):
    """A site is the top-level object that holds, well, all contents
    of the web site.
    """

    meta_type = 'Site'
    label = 'Site' # FIXME: needed?

    __parent__ = __name__ = None

    def __init__(self):
        from petrel.auth import create_user_db # FIXME: not nice but ok
        Folder.__init__(self)
        create_catalog_tools(self)
        create_user_db(self)
        self.title = u'Site'
        self.description = u'A site.'
#        self.index() # for 'utils.get_nav_tree()' to work properly ## FIXME: really?
