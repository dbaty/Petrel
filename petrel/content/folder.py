"""Define the Folder content type and everything related to it: forms,
views, etc.

$Id$
"""

from repoze.bfg.threadlocal import get_current_registry

from repoze.folder import Folder as BaseFolder
from repoze.folder.events import ObjectAddedEvent
from repoze.folder.events import ObjectWillBeRemovedEvent

from wtforms.fields import TextField
from wtforms.validators import required

from zope.interface import implements

from petrel.content.base import BaseContent
from petrel.content.base import BaseForm
from petrel.interfaces import IFolderish
from petrel.views import get_default_view_bindings
from petrel.views import redirect_to


class Folder(BaseFolder, BaseContent):
    implements(IFolderish)

    def __init__(self, *args, **kwargs):
        BaseContent.__init__(self)
        BaseFolder.__init__(self, *args, **kwargs)

    def add(self, name, obj):
        ## We fire events ourselves because 'repoze.folder' uses the
        ## global ZCA registry. We use the BFG registry instead.
        res = BaseFolder.add(self, name, obj, send_events=False)
        registry = get_current_registry()
        registry.notify(ObjectAddedEvent(obj, self, name))
        return res

    def remove(self, name):
        ## Cf. add() about firing events ourselves.
        obj = self[name]
        registry = get_current_registry()
        registry.notify(ObjectWillBeRemovedEvent(obj, self, name))
        res = BaseFolder.remove(self, name, send_events=False)
        return res

    def get_addable_types(self):
        ## FIXME: make this configurable
        return ('folder', 'document')


class FolderEditForm(BaseForm):
    ## FIXME: check that id is not already taken
    id = TextField(label=u'Id',
                   description=u'Should be short, will be part of the URL.',
                   validators=[required()])
    title = TextField(label=u'Title', validators=[required()])


def folder_view(request):
    return get_default_view_bindings(request)


def folder_add_form(request, form=None):
    bindings = get_default_view_bindings(request)
    if form is None:
        form = FolderEditForm()
    bindings.update(action='addFolder',
                    content_type='folder',
                    add_mode=True,
                    form=form)
    return bindings


def folder_add(request):
    form = FolderEditForm(request.POST)
    if not form.validate():
        return folder_add_form(request, form)

    folder = Folder()
    folder.edit(title=form.title.data)
    request.context.add(form.id.data, folder)
    msg = (u'Folder "%s" has been created and you are '
           'now viewing it.' % form.title.data)
    return redirect_to(folder.get_url(request), status_message=msg)


def folder_action_handler(request):
    ## FIXME: use 'request_param' in the view directive instead
    ## (cf.http://docs.repoze.org/bfg/1.3/narr/views.html#predicate-arguments)
    action = request.POST['action']
    if action == 'delete':
        return folder_delete(request)
    else:
        raise ValueError(u'Unexpected action')


def folder_delete(request):
    folder = request.context
    for name in request.POST.getall('selected'):
        folder.remove(name)
    msg = u'Item(s) have been deleted.'
    return redirect_to(folder.get_url(request), status_message=msg)
