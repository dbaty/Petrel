from zope.interface import Interface


class IFolderish(Interface):
    """An item that may contain other items."""


class ICatalogAware(Interface):
    """An item that is cataloged."""


class IContentTypeRegistry(Interface):
    """Petrel content type registry."""


class ITemplateAPI(Interface):
    """Petrel template API class."""


class IObjectModifiedEvent(Interface):
    """Event sent when an object is modified."""
