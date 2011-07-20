from zope.interface import implements

from petrel.interfaces import IContentTypeRegistry


class ContentTypeRegistry(dict):
    implements(IContentTypeRegistry)


def get_content_type_registry(pyramid_registry):
    """Return Petrel content type registry."""
    reg = pyramid_registry.queryUtility(IContentTypeRegistry, default=None)
    if reg is None:
        reg = ContentTypeRegistry()
        pyramid_registry.registerUtility(reg, IContentTypeRegistry)
    return reg
