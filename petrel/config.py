from pyramid.configuration import Configurator

from repoze.zodbconn.finder import PersistentApplicationFinder

from petrel.content.site import Site


def app_maker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Site()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']


def get_default_config(app_maker=app_maker, **settings):
    """Provide a default configuration for a Petrel-based
    application.
    """
    zodb_uri = settings.get('zodb_uri')
    if not zodb_uri:
        raise ValueError("No 'zodb_uri' in application configuration.")
    finder = PersistentApplicationFinder(zodb_uri, app_maker)
    def get_root(request):
        return finder(request.environ)
    config = Configurator(root_factory=get_root, settings=settings)

    ## Register default content types
    from petrel.content.document import Document
    from petrel.content.folder import Folder
    from petrel.content.site import Site
    from petrel.content.registry import register_content_type
    config.add_static_view(name='static', path='static')
    ## FIXME: we should not define any view template
    register_content_type(config,
                          klass=Site,
                          display_view_template='petrel:templates/folder.pt')
    register_content_type(config,
                          klass=Folder,
                          display_view_template='petrel:templates/folder.pt')
    ## FIXME: folder actions are missing (delete, rename, etc.)
#   <view context=".interfaces.IFolderish"
#         name="folder_action_handler"
#         request_param="action=delete"
#         view=".content.folder.folder_delete"/>
#   <view context=".interfaces.IFolderish"
#         name="folder_action_handler"
#         request_param="action=rename"
#         view=".content.folder.folder_rename_form"
#         renderer="templates/folder_rename.pt"/>
#   <view context=".interfaces.IFolderish"
#         name="rename"
#         view=".content.folder.folder_rename"/>

    register_content_type(config,
                          klass=Document,
                          display_view_template='petrel:templates/document.pt')

    ## Register default subscribers
    from repoze.folder.interfaces import IObjectAddedEvent
    from repoze.folder.interfaces import IObjectWillBeRemovedEvent
    from petrel.catalog import index
    from petrel.catalog import reindex
    from petrel.catalog import unindex
    ## FIXME: why do I use my own event?
    from petrel.interfaces import IObjectModifiedEvent
    config.add_subscriber(index, IObjectAddedEvent)
    config.add_subscriber(reindex, IObjectModifiedEvent)
    config.add_subscriber(unindex, IObjectWillBeRemovedEvent)

    ## FIXME: shall we register the search form?
    return config
