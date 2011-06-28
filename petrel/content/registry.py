"""Utilities to register content types.

$Id$
"""

from zope.interface import implements

from pyramid.threadlocal import get_current_registry

from petrel.interfaces import IContentTypeRegistry
from petrel.interfaces import IFolderish


class ContentTypeRegistry(dict):
    implements(IContentTypeRegistry)


def get_content_type_registry(pyramid_registry=None):
    """Return Petrel content type registry."""
    if pyramid_registry is None: ## FIXME: do we need this?
        pyramid_registry = get_current_registry()
    reg = pyramid_registry.queryUtility(IContentTypeRegistry, default=None)
    if reg is None:
        reg = ContentTypeRegistry()
        pyramid_registry.registerUtility(reg, IContentTypeRegistry)
    return reg


## FIXME: values of the registry should not be dictionaries, but
## rather a specific class.
## FIXME: not sure that it belongs to the registry module.
def register_content_type(config,
                          klass,
                          display_view_template,
                          display_view=None,
                          add_form_view=None,
                          add_form_template=None,
                          add_view=None,
                          edit_form_view=None,
                          edit_form_template=None,
                          edit_view=None):
    """FIXME: document args"""
    from petrel.content.base import content_add
    from petrel.content.base import content_add_form
    from petrel.content.base import content_edit
    from petrel.content.base import content_edit_form
    from petrel.content.base import content_view

    if display_view is None:
        display_view = content_view
        if display_view_template is None:
            raise ValueError(
                'Content type "%s" uses default display view but '
                'does not define any template. A template is '
                'required in this case.' % klass)
    if add_form_view is None:
        add_form_view = lambda request, form=None: content_add_form(
            klass, request, form)
        if add_form_template is None:
            add_form_renderer = 'templates/content_edit.pt'
    if add_view is None:
        add_view = lambda request: content_add(klass, request)
    if edit_form_view is None:
        edit_form_view = content_edit_form
        if edit_form_template is None:
            edit_form_renderer = 'templates/content_edit.pt'
    if edit_view is None:
        edit_view = content_edit

    ## Register views
    config.add_view(name='%s_add_form' % klass.meta_type.lower(),
                    context=IFolderish,
                    view=add_form_view,
                    renderer=add_form_renderer)
    ## The 'renderer' attribute below is needed when the view has to
    ## redisplay the add form.
    config.add_view(name='add%s' % klass.meta_type,
                    context=IFolderish,
                    request_method='POST',
                    view=add_view,
                    renderer=add_form_renderer)
    config.add_view(context=klass,
                    view=display_view,
                    renderer=display_view_template)
    config.add_view(name='edit_form',
                    context=klass,
                    view=edit_form_view,
                    renderer=edit_form_renderer)
    ## The 'renderer' attribute below is needed when the view has to
    ## redisplay the edit form.
    config.add_view(name='edit',
                    context=klass,
                    request_method='POST',
                    view=edit_view,
                    renderer=edit_form_renderer)

    ## Register the content type in our content type registry.
    ct_registry = get_content_type_registry(config.registry)
    ct_registry[klass.meta_type] = dict(
        label=klass.label,
        add_form_view=add_form_view,
        edit_form_view=edit_form_view,
        display_view_template=display_view_template)
