"""Define the Folder content type and everything related to it: forms,
views, etc.

$Id$
"""

from repoze.bfg.threadlocal import get_current_registry

from repoze.folder import Folder as BaseFolder
from repoze.folder.events import ObjectAddedEvent
from repoze.folder.events import ObjectWillBeRemovedEvent

from zope.interface import implements

from petrel.content.base import BaseContent
from petrel.content.base import BaseContentAddForm
from petrel.content.base import BaseContentEditForm
from petrel.content.registry import get_content_type_registry
from petrel.interfaces import IFolderish
from petrel.views import redirect_to


class FolderAddForm(BaseContentAddForm, ):
    pass


class FolderEditForm(BaseContentEditForm, FolderAddForm):
    pass


class Folder(BaseFolder, BaseContent):
    implements(IFolderish)

    meta_type = 'Folder'
    label = 'Folder'
    icon = 'static/img/folder.gif'

    add_form = FolderAddForm
    edit_form = FolderEditForm

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
        ct_registry = get_content_type_registry()
        return [(ct['label'], '%s_add_form' % meta_type.lower()) \
                    for meta_type, ct in ct_registry.items()]

    def validate_id(self, obj_id):
        """Validate that ``obj_id`` is a valid id in this folderish
        item.
        """
        return obj_id not in self


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
