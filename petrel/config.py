from pyramid.configuration import Configurator as Base

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


## FIXME: perhaps we could use 'pyramid.Configurator.add_directive()'
## instead of subclassing.
class Configurator(Base):

    def customize_content_type(self, klass,
                               display_view=None,
                               display_view_template=None):
        registry = self.registry.queryUtility(IContentTypeRegistry)
        entry = registry[klass]
        if display_view_template is not None:
            entry['display_view'] = display_view
        if display_view_template is not None:
            entry['display_view_template'] = display_view_template


    def registerTemplateAPI(self, factory): ## FIXME: naming
        self.registry.registerUtility(factory, ITemplateAPI)


    def register_content_type(self,
                              klass,
                              display_view_template=None,
                              display_view=None,
                              add_form_view=None,
                              add_form_template=None,
                              add_view=None,
                              edit_form_view=None,
                              edit_form_template=None,
                              edit_view=None):
        """FIXME: document args"""
        ## FIXME: those views should probably be moved elsewhere.
        from petrel.content.base import content_add
        from petrel.content.base import content_add_form
        from petrel.content.base import content_edit
        from petrel.content.base import content_edit_form
        from petrel.content.base import content_view
        from petrel.views import toolbar

        ## FIXME: review these blocks.
        if display_view is None:
            display_view = content_view
            if display_view_template is None:
                display_view_template = '-- this template should have been customized--' ## FIXME: really?
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
        ## FIXME: check that we still need all this.
        ## The 'renderer' attribute below is needed when the view has
        ## to redisplay the add form.
        self.add_view(name='add_%s' % klass.meta_type.lower(),
                      context=IFolderish,
                      request_method='POST',
                      view=add_view,
                      renderer=add_form_renderer)
        self.add_view(name='add_%s' % klass.meta_type.lower(),
                      context=IFolderish,
                      view=add_form_view,
                      renderer=add_form_renderer)
        self.add_view(context=klass,
                      view=display_view,
                      renderer=display_view_template)
        self.add_view(name='edit',
                      context=klass,
                      view=edit_form_view,
                      renderer=edit_form_renderer)
        ## The 'renderer' attribute below is needed when the view has
        ## to redisplay the edit form.
        self.add_view(name='edit',
                      context=klass,
                      request_method='POST',
                      view=edit_view,
                      renderer=edit_form_renderer)
        self.add_view(name='_toolbar.html',
                      renderer='petrel:templates/toolbar.pt',
                      view=toolbar)

        ## Register the content type in our content type registry.
        ct_registry = get_content_type_registry(self.registry)
        ct_registry[klass] = dict(
            label=klass.label,
            add_form_view=add_form_view,
            edit_form_view=edit_form_view,
            display_view_template=display_view_template)


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

    ## Register default content types
    from petrel.content.document import Document
    from petrel.content.folder import Folder
    from petrel.content.folder import folder_contents
    from petrel.content.site import Site
    ## FIXME: look at the new cache_max_age argument
    config.add_static_view(name='static-petrel', path='petrel:static')
    ## FIXME: we should not define any view template
    config.register_content_type(Site)
    config.register_content_type(Folder)
    config.register_content_type(Document)
    config.add_view(name='contents',
                    context=IFolderish,
                    view=folder_contents,
                    renderer='templates/folder_contents.pt')
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

    return config
