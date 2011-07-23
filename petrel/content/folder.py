import re

from pyramid.httpexceptions import HTTPSeeOther

from repoze.folder import Folder as BaseFolder
from repoze.folder import unicodify
from repoze.folder.events import ObjectAddedEvent
from repoze.folder.events import ObjectWillBeRemovedEvent

from wtforms.fields import TextAreaField

from zope.interface import implements

from petrel.content.base import BaseContent
from petrel.content.registry import get_content_type_registry
from petrel.forms import BaseContentAddForm
from petrel.forms import BaseContentEditForm
from petrel.interfaces import IFolderish
from petrel.views.utils import get_template_api


ALLOWED_NAME = re.compile('^[a-zA-Z0-9]+[\w.-]*$')
FORBIDDEN_NAMES = ('folder_add_form', 'document_add_form',
                   'addFolder', 'addDocument',
                   'edit_form', 'edit',
                   'search_form', 'search',
                   'sitemap')


class FolderAddForm(BaseContentAddForm, ):
    body = TextAreaField(label=u'Body')


class FolderEditForm(BaseContentEditForm, FolderAddForm):
    pass


class Folder(BaseFolder, BaseContent):
    implements(IFolderish)

    meta_type = 'Folder'
    label = 'Folder'
    is_folderish = True
    icon = 'petrel:static/img/type_folder.png'

    body = u''

    add_form = FolderAddForm
    edit_form = FolderEditForm

    def __init__(self, *args, **kwargs):
        BaseContent.__init__(self)
        BaseFolder.__init__(self, *args, **kwargs)

    def add(self, registry, name, obj):
        ## We fire events ourselves because 'repoze.folder' uses the
        ## global ZCA registry. Here we use Pyramid registry instead.
        res = BaseFolder.add(self, name, obj, send_events=False)
        registry.notify(ObjectAddedEvent(obj, self, name))
        return res

    def remove(self, registry, name):
        ## Cf. add() about firing events ourselves.
        obj = self[name]
        registry.notify(ObjectWillBeRemovedEvent(obj, self, name))
        res = BaseFolder.remove(self, name, send_events=False)
        return res

    def rename(self, registry, names):
        for old_name, new_name in names:
            old_name = unicodify(old_name)
            new_name = unicodify(new_name)
            if new_name in self:
                raise ValueError(
                    u'An item of the same name ("%s") already '
                    'exists.' % new_name)
            obj = self.remove(registry, old_name)
            self.add(registry, new_name, obj)
        return True

    def validate_id(self, obj_id):
        """Validate that ``obj_id`` is a valid id in this folderish
        item.
        """
        if not ALLOWED_NAME.match(obj_id):
            return False
        if obj_id in FORBIDDEN_NAMES:
            return False
        return obj_id not in self

    def get_addable_types(self, request):
        ct_registry = get_content_type_registry(request.registry)
        return [(ct['label'], 'add_%s' % meta_type.lower()) \
                    for meta_type, ct in ct_registry.items()]


def folder_contents(request):
    return {'api': get_template_api(request),
            'items': request.context.values(),
            'load_jquery': False,
            'load_editor': False}


def folder_delete(request):
    folder = request.context
    selected = request.POST.getall('selected')
    if not selected:
        msg = u'No items were selected.'
        request.session.flash(msg, 'error')
    else:
        for name in selected:
            folder.remove(request.registry, name)
        msg = u'Item(s) have been deleted.'
        request.session.flash(msg, 'success')
    return HTTPSeeOther('%scontents' % request.resource_url(folder))


def folder_rename_form(request):
    folder = request.context
    names = request.POST.getall('selected')
    if not names:
        msg = u'No items were selected.'
        request.session.flash(msg, 'error')
        return HTTPSeeOther('%scontents' % request.resource_url(folder))
    items = [{'id': name,
              'title': folder[name].title} \
                 for name in names]
    return {'api': get_template_api(request),
            'items': items,
            'load_jquery': False,
            'load_editor': False}


def folder_rename(request):
    folder = request.context
    ## FIXME: check that 'name_orig' is valid
    ## FIXME: check that 'name_new' is valid
    names = []
    for i in range(len(request.POST.getall('name_orig'))):
        names.append((request.POST.getall('name_orig')[i],
                      request.POST.getall('name_new')[i]))
    try:
        folder.rename(request.registry, names)
    except ValueError:
        raise # FIXME: show error message.
    msg = u'Item(s) have been renamed.'
    request.session.flash(msg, 'success')
    return HTTPSeeOther('%scontents' % request.resource_url(folder))
