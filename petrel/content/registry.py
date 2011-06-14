"""Utilities to register content types.

$Id$
"""

from zope.interface import implements

from pyramid.threadlocal import get_current_registry

from petrel.interfaces import IContentTypeRegistry


class ContentTypeRegistry(dict):
    implements(IContentTypeRegistry)

## FIXME: values of the registry should not be dictionaries, but
## rather a specific class.


def get_content_type_registry(pyramid_registry=None):
    """Return Petrel content type registry."""
    if pyramid_registry is None:
        pyramid_registry = get_current_registry()
    reg = pyramid_registry.queryUtility(IContentTypeRegistry, default=None)
    if reg is None:
        reg = ContentTypeRegistry()
        pyramid_registry.registerUtility(reg, IContentTypeRegistry)
    return reg
