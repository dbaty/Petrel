"""Define Petrel ZCML directive.

$Id$
"""

from repoze.bfg.configuration import Configurator
from repoze.bfg.threadlocal import get_current_registry

from zope.configuration.fields import GlobalObject

from zope.interface import Interface

from zope.schema import TextLine

from petrel.content.base import content_add
from petrel.content.base import content_add_form
from petrel.content.base import content_edit
from petrel.content.base import content_edit_form
from petrel.content.base import content_view
from petrel.content.registry import get_content_type_registry
from petrel.interfaces import IFolderish


class IContentTypeDirective(Interface):
    """Describe the ``<content_type>`` ZCML directive."""
    klass = GlobalObject(
        title=u'The class of the content type.',
        required=True)
    display_view = GlobalObject(
        title=u'The view that is called to display the item.',
        required=False)
    ## We sure could have provided a default view template but,
    ## usually, the template is customized anyway.
    display_view_renderer = TextLine(
        title=u'The (optional) template used when displaying the item.',
        required=True)
    add_form_view = GlobalObject(
        title=u'The view that is called to display the add form',
        required=False)
    add_form_renderer = TextLine(
        title=u'The (optional) template used to render the add form view.',
        required=False)
    add_view = GlobalObject(
        title=u'The view that is called to add an item.',
        required=False)
    edit_form_view = GlobalObject(
        title=u'The view that is called to display the edit form',
        required=False)
    edit_form_renderer = TextLine(
        title=u'The (optional) template used to render the edit form view.',
        required=False)
    edit_view = GlobalObject(
        title=u'The view that is called to edit an item.',
        required=False)


def _register_content_type(_context, **kwargs):
    """Handler of the ``<content_type>`` ZCML directive."""
    _context.action(
        discriminator=None,
        callable=register_content_type,
        kw=kwargs)


## FIXME: we should try to move this functionto the 'registry' module
## (or perhaps the 'ContentTypeRegistry' class).
def register_content_type(klass,
                          display_view_renderer,
                          display_view=None,
                          add_form_view=None,
                          add_form_renderer=None,
                          add_view=None,
                          edit_form_view=None,
                          edit_form_renderer=None,
                          edit_view=None):
    """FIXME: document args"""
    if display_view is None:
        display_view = content_view
        if display_view_renderer is None:
            raise ValueError(
                'Content type "%s" uses default display view but '
                'does not define any renderer. A renderer is '
                'required in this case.' % klass)
    if add_form_view is None:
        add_form_view = lambda request, form=None: content_add_form(
            klass, request, form)
        if add_form_renderer is None:
            add_form_renderer = 'templates/content_edit.pt'
    if add_view is None:
        add_view = lambda request: content_add(klass, request)
    if edit_form_view is None:
        edit_form_view = content_edit_form
        if edit_form_renderer is None:
            edit_form_renderer = 'templates/content_edit.pt'
    if edit_view is None:
        edit_view = content_edit

    ## Register views
    ## FIXME: is this the right way to do it?
    config = Configurator(registry=get_current_registry())
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
                    renderer=display_view_renderer)
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
    ct_registry = get_content_type_registry()
    ct_registry[klass.meta_type] = dict(
        label=klass.label,
        add_form_view=add_form_view,
        edit_form_view=edit_form_view)
