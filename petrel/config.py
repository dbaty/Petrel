from pyramid.config import Configurator

from pyramid_beaker import session_factory_from_settings

from repoze.zodbconn.finder import PersistentApplicationFinder

from petrel.content.registry import get_content_type_registry
from petrel.content.site import Site
from petrel.interfaces import IContentTypeRegistry
from petrel.interfaces import IFolderish
from petrel.interfaces import ITemplateAPI


def app_maker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Site()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']


def _register_template_api(config, factory):
    config.registry.registerUtility(factory, ITemplateAPI)


def _register_content_type(config,
                           klass,
                           display_view=None,
                           display_templates=None,
                           add_form_view=None,
                           add_template=None,
                           add_view=None,
                           edit_form_view=None,
                           edit_template=None,
                           edit_view=None):
    """FIXME: document args"""
    from petrel.content.base import content_add
    from petrel.content.base import content_add_form
    from petrel.content.base import content_edit
    from petrel.content.base import content_edit_form
    from petrel.content.base import content_view

    ## Default views
    if display_view is None:
        display_view = content_view
        if display_templates is None:
            display_templates = {}
    if add_form_view is None:
        add_form_view = lambda request, form=None: content_add_form(
            klass, request, form)
        if add_template is None:
            add_template = 'templates/content_edit.pt'
    if add_view is None:
        add_view = lambda request: content_add(klass, request)
    if edit_form_view is None:
        edit_form_view = content_edit_form
        if edit_template is None:
            edit_template = 'templates/content_edit.pt'
    if edit_view is None:
        edit_view = content_edit

    ## Register views
    ## The 'renderer' attribute below is needed when the view has
    ## to redisplay the add form.
    config.add_view(name='add_%s' % klass.meta_type.lower(),
                    context=IFolderish,
                    request_method='POST',
                    view=add_view,
                    renderer=add_template)
    config.add_view(name='add_%s' % klass.meta_type.lower(),
                    context=IFolderish,
                    view=add_form_view,
                    renderer=add_template)
    config.add_view(context=klass,
                    view=display_view)
    config.add_view(name='edit',
                    context=klass,
                    view=edit_form_view,
                    renderer=edit_template)
    ## The 'renderer' attribute below is needed when the view has
    ## to redisplay the edit form.
    config.add_view(name='edit',
                    context=klass,
                    request_method='POST',
                    view=edit_view,
                    renderer=edit_template)

    ## Register the content type in our content type registry.
    ct_registry = get_content_type_registry(config.registry)
    ct_registry[klass] = dict(
        add_form_view=add_form_view,
        edit_form_view=edit_form_view,
        display_templates=display_templates)


def _customize_content_type(config, klass, **kwargs):
    registry = config.registry.queryUtility(IContentTypeRegistry)
    entry = registry[klass]
    entry.update(kwargs)


## FIXME: the name of the method does not sound right.
## FIXME: arguments do not sound right either...
def get_default_config(base_config=None, **settings):
    """Provide a default configuration for a Petrel-based
    application.
    """
    if base_config is not None:
        config = base_config
    else:
        zodb_uri = settings.get('zodb_uri')
        if not zodb_uri:
            raise ValueError("No 'zodb_uri' in application configuration.")
        finder = PersistentApplicationFinder(zodb_uri, app_maker)
        def get_root(request):
            return finder(request.environ)
        session_factory = session_factory_from_settings(settings)
        config = Configurator(root_factory=get_root,
                              session_factory=session_factory,
                              settings=settings)

    config.add_directive('register_template_api', _register_template_api)
    config.add_directive('register_content_type', _register_content_type)
    config.add_directive('customize_content_type', _customize_content_type)

    ## Register default content types
    from petrel.content.document import Document
    from petrel.content.file import File
    from petrel.content.folder import Folder
    from petrel.content.folder import folder_contents
    from petrel.content.folder import folder_delete
    from petrel.content.folder import folder_rename
    from petrel.content.folder import folder_rename_form
    from petrel.content.site import Site
    from petrel.views.admin import toolbar
    ## FIXME: look at the new cache_max_age argument
    config.add_static_view(name='static-petrel', path='petrel:static')
    config.register_content_type(Site)
    config.register_content_type(Folder)
    config.register_content_type(Document)
    config.register_content_type(File) # FIXME: we need extra views!
    config.add_view(name='contents',
                    context=IFolderish,
                    view=folder_contents,
                    renderer='templates/folder_contents.pt')
    config.add_view(name='folder_action_handler',
                    context='petrel.interfaces.IFolderish',
                    request_param="action=delete",
                    view=folder_delete)
    config.add_view(name='folder_action_handler',
                    context='petrel.interfaces.IFolderish',
                    request_param='action=rename',
                    view=folder_rename_form,
                    renderer='templates/folder_rename.pt')
    config.add_view(name='rename',
                    context='petrel.interfaces.IFolderish',
                    view=folder_rename)
    config.add_view(name='_toolbar.html',
                    renderer='petrel:templates/toolbar.pt',
                    view=toolbar)

    ## Register default subscribers
    from repoze.folder.interfaces import IObjectAddedEvent
    from repoze.folder.interfaces import IObjectWillBeRemovedEvent
    from petrel.search import index
    from petrel.search import reindex
    from petrel.search import unindex
    from petrel.interfaces import IObjectModifiedEvent
    config.add_subscriber(index, IObjectAddedEvent)
    config.add_subscriber(reindex, IObjectModifiedEvent)
    config.add_subscriber(unindex, IObjectWillBeRemovedEvent)

    return config
