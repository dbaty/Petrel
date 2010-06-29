from zope.interface import Interface


class IFolderish(Interface):
    """Marker interface."""


class ICatalogAware(Interface):
    """Marker interface."""


class IObjectModifiedEvent(Interface):
    """Sent when an object is modified."""
