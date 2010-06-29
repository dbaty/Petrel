from persistent import Persistent

from repoze.bfg.location import lineage
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.url import model_url

from wtforms.form import Form

from petrel.catalog import CatalogAware
from petrel.events import ObjectModifiedEvent


class BaseContent(Persistent, CatalogAware):

    def __init__(self):
        Persistent.__init__(self)
        self.title = u''
        self.description = u''

    def get_searchable_text(self):
        return u' '.join((self.title, self.description))

    def edit(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if getattr(self, '__parent__', None):
            ## Notify only if object has been added already.
            registry = get_current_registry()
            registry.notify(ObjectModifiedEvent(self))

    def get_url(self, request):
        return model_url(self, request).strip('/')

    def get_breadcrumbs(self):
        ## FIXME: this is slighty more complicated than this. We
        ## should return the default page of each parent in the
        ## lineage, something like: reversed([obj.getDefaultItem() for
        ## obj in lineage])
        return list(lineage(self))[::-1]


class BaseForm(Form):
    """A base class for all forms in Petrel."""
    pass
