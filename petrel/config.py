from pyramid.config import Configurator

from pyramid_beaker import session_factory_from_settings

from repoze.zodbconn.finder import PersistentApplicationFinder

from petrel.content.registry import get_content_type_registry
from petrel.interfaces import IContentTypeRegistry
from petrel.interfaces import IFolderish
from petrel.interfaces import ITemplateAPI


# FIXME: do we need to include import statements in the functions or
# could they be moved at module scope?

SITE_ID = 'site'

def app_maker(zodb_root):
    if SITE_ID not in zodb_root:
        from petrel.content.site import Site
        site = Site()
        zodb_root[SITE_ID] = site
        import transaction
        transaction.commit()
    return zodb_root[SITE_ID]


def _register_template_api(config, factory):
    config.registry.registerUtility(factory, ITemplateAPI)


def _register_content_type(config,
                           klass,
                           addable=True,
                           display_view=None,
                           display_templates=(),
                           add_form_view=None,
                           add_template=None,
                           add_view=None,
                           edit_form_view=None,
                           edit_template=None,
                           edit_view=None,
                           extra_views=()):
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
            display_templates = ()
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
    if addable:
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
    for extra_view in extra_views:
        config.add_view(**extra_view)

    ## Register the content type in our content type registry.
    ct_registry = get_content_type_registry(config.registry)
    ct_registry[klass] = dict(
        addable=addable,
        add_form_view=add_form_view,
        edit_form_view=edit_form_view,
        display_templates=display_templates)


def _customize_content_type(config, klass, **kwargs):
    registry = config.registry.queryUtility(IContentTypeRegistry)
    entry = registry[klass]
    extra_views = kwargs.pop('extra_views', ())
    entry.update(kwargs)
    for extra_view in extra_views:
        config.add_view(**extra_view)


## FIXME: the name of the method does not sound right.
## FIXME: arguments do not sound right either...
def get_default_config(global_config, base_config=None, **settings):
    """Provide a default configuration for a Petrel-based
    application.
    """
    if base_config is not None:
        config = base_config
    else:
        zodb_uri = settings.get('zodb_uri', None) or \
            global_config.get('zodb_uri', None)
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
    from petrel.content.file import file_download
    from petrel.content.folder import Folder
    from petrel.content.folder import folder_contents
    from petrel.content.folder import folder_delete
    from petrel.content.folder import folder_rename
    from petrel.content.folder import folder_rename_form
    from petrel.content.image import Image
    from petrel.content.site import Site
    from petrel.views.admin import toolbar
    ## FIXME: look at the new cache_max_age argument
    config.add_static_view(name='static-petrel', path='petrel:static')
    config.register_content_type(Site, addable=False)
    config.register_content_type(Document)
    config.register_content_type(
        File,
        display_view=file_download)
    config.register_content_type(
        Image,
        display_view=file_download)
    config.register_content_type(Folder)
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

    ## Enable authorization system and related views
    from petrel.auth import setup_who_api_factory
    from petrel.views.auth import login
    from petrel.views.auth import login_form
    from petrel.views.auth import logout
    setup_who_api_factory(global_config, settings['auth_config_file'])
    config.add_view(name='login',
                    renderer='petrel:templates/login.pt',
                    view=login_form)
    config.add_view(name='login',
                    request_method='POST',
                    renderer='petrel:templates/login.pt',
                    view=login)
    config.add_view(name='logout',
                    view=logout)

    return config
