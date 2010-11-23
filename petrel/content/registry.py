"""Utilities to register content types.

$Id$
"""

from zope.interface import implements

from pyramid.threadlocal import get_current_registry

from petrel.interfaces import IContentTypeRegistry


class ContentTypeRegistry(dict):
    implements(IContentTypeRegistry)


def get_content_type_registry():
    pyramid_registry = get_current_registry()
    reg = pyramid_registry.queryUtility(IContentTypeRegistry, default=None)
    if reg is None:
        reg = ContentTypeRegistry()
        pyramid_registry.registerUtility(reg, IContentTypeRegistry)
    return reg
