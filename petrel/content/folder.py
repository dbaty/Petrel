"""Define the Folder content type and everything related to it: forms,
views, etc.

$Id$
"""

import re

from pyramid.threadlocal import get_current_registry

from repoze.folder import Folder as BaseFolder
from repoze.folder import unicodify
from repoze.folder.events import ObjectAddedEvent
from repoze.folder.events import ObjectWillBeRemovedEvent

from zope.interface import implements

from petrel.content.base import BaseContent
from petrel.content.base import BaseContentAddForm
from petrel.content.base import BaseContentEditForm
from petrel.interfaces import IFolderish
from petrel.views import get_default_view_bindings
from petrel.views import redirect_to


ALLOWED_NAME = re.compile('^[a-zA-Z0-9]+[\w.-]*$')
FORBIDDEN_NAMES = ('folder_add_form', 'document_add_form',
                   'addFolder', 'addDocument',
                   'edit_form', 'edit',
                   'search_form', 'search',
                   'sitemap')

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

    def rename(self, names):
        for old_name, new_name in names:
            old_name = unicodify(old_name)
            new_name = unicodify(new_name)
            if new_name in self:
                raise ValueError(
                    u'An item of the same name ("%s") already '
                    'exists.' % new_name)
            obj = self.remove(old_name)
            self.add(new_name, obj)
        return True

## FIXME: move elsewhere
#    def get_addable_types(self, registry):
#        ct_registry = get_content_type_registry(registry)
#        return [(ct['label'], '%s_add_form' % meta_type.lower()) \
#                    for meta_type, ct in ct_registry.items()]

    def validate_id(self, obj_id):
        """Validate that ``obj_id`` is a valid id in this folderish
        item.
        """
        if not ALLOWED_NAME.match(obj_id):
            return False
        if obj_id in FORBIDDEN_NAMES:
            return False
        return obj_id not in self


def folder_delete(request):
    folder = request.context
    for name in request.POST.getall('selected'):
        folder.remove(name)
    msg = u'Item(s) have been deleted.'
    return redirect_to(folder.get_url(request), status_message=msg)


def folder_rename_form(request):
    bindings = get_default_view_bindings(request)
    names = request.POST.getall('selected')
    bindings.update(items=[{'id': name,
                            'title': request.context[name].title} \
                               for name in names])
    return bindings


def folder_rename(request):
    context = request.context
    ## FIXME: check that 'name_orig' is valid
    ## FIXME: check that 'name_new' is valid
    names = []
    for i in range(len(request.POST.getall('name_orig'))):
        names.append((request.POST.getall('name_orig')[i],
                      request.POST.getall('name_new')[i]))
    try:
        context.rename(names)
    except ValueError:
        raise ## FIXME: show error message.
    msg = u'Item(s) have been renamed.'
    return redirect_to(context.get_url(request), status_message=msg)
