from persistent import Persistent

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.threadlocal import get_current_registry

from wtforms.fields import TextField
from wtforms.form import Form
from wtforms.validators import required

from petrel.catalog import CatalogAware
from petrel.content.registry import get_content_type_registry
from petrel.events import ObjectModifiedEvent
from petrel.views import get_default_view_bindings


class BaseContent(Persistent, CatalogAware):

    is_folderish = False

    title = u''
    description = u''

    @classmethod
    def _get_add_form(cls, *args, **kwargs):
        return cls.add_form(*args, **kwargs)

    def _get_edit_form(self, request_data=None):
        if request_data is None:
            form_class = self.edit_form
            data = {}
            for field in form_class():
                ## We create a fake form to get its fields. There are
                ## other ways but this probably is the easiest one.
                data[field.name] = getattr(self, field.name)
            return form_class(**data)
        return self.edit_form(request_data)

    def get_searchable_text(self):
        return u' '.join((self.title, self.description))

    def edit(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if getattr(self, '__parent__', None):
            ## Notify only if object has been added already.
            registry = get_current_registry()
            registry.notify(ObjectModifiedEvent(self))

    def get_addable_types(self, request):
        return ()


class BaseForm(Form):
    def validate(self, context=None):
        """Validate form.

        ``context`` is to be given **if and only if** this is an add
        form and we must therefore validate the given id.
        """
        success = Form.validate(self)
        if context:
            if not context.validate_id(self.id.data):
                success = False
                self.id.errors.append(
                    u'An item with the same id already exists.')
        return success


class BaseContentAddForm(BaseForm):
    """A base class for all add forms in Petrel."""

    ## FIXME: all TextField and TextAreaField should be sanitized.
    id = TextField(label=u'Id',
                   description=u'Should be short, will be part of the URL.',
                   validators=[required()])
    title = TextField(label=u'Title', validators=[required()])

    def populate_obj(self, obj):
        data = self.data
        self.data.pop('id', None)
        obj.edit(**data)


class BaseContentEditForm:
    """A mix-in class for all edit forms in Petrel.

    Typically the edit form of a content type derives from its add
    form (which includes ``id``) and this mix-in (which does not).
    """
    id = None


## FIXME: move this elsewhere
from petrel.interfaces import ITemplateAPI
def get_template_api(request):
    factory = request.registry.queryUtility(ITemplateAPI)
    return factory(request)


def content_view(request):
    ct_registry = get_content_type_registry(request.registry)
    template = ct_registry[request.context.__class__]['display_view_template']
    api = get_template_api(request)
    return render_to_response(template,
                              {'api': api, 'context': request.context})


def content_add_form(content_type, request, form=None):
    bindings = get_default_view_bindings(request)
    if form is None:
        form = content_type._get_add_form()
    ct_registry = get_content_type_registry(request.registry)
    label = ct_registry[content_type]['label']
    bindings.update(load_jquery=True,
                    load_editor=True,
                    content_type=label,
                    add_mode=True,
                    form=form)
    return bindings


def content_add(content_type, request):
    context = request.context
    form = content_type._get_add_form(request.POST)
    form.errors['id'] = [u'Invalid id']
    if not form.validate(context):
        ct_registry = get_content_type_registry(request.registry)
        add_form_view = ct_registry[content_type]['add_form_view']
        return add_form_view(request, form)
    item = content_type()
    form.populate_obj(item)
    context.add(form.id.data, item)
    ct_registry = get_content_type_registry(request.registry)
    label = ct_registry[content_type]['label']
    msg = (u'%s "%s" has been created and you are '
           'now viewing it.' % (label, form.title.data))
    request.session.flash(msg, 'success')
    return HTTPSeeOther(request.resource_url(item))


def content_edit_form(request, form=None):
    context = request.context
    content_type = context.__class__
    bindings = get_default_view_bindings(request)
    if form is None:
        form = context._get_edit_form()
    ct_registry = get_content_type_registry(request.registry)
    label = ct_registry[content_type]['label']
    bindings.update(load_jquery=True,
                    load_editor=True,
                    content_type=label,
                    add_mode=False,
                    form=form)
    return bindings


def content_edit(request):
    item = request.context
    form = item._get_edit_form(request.POST)
    if not form.validate():
        ct_registry = get_content_type_registry(request.registry)
        edit_form_view = ct_registry[item]['edit_form_view']
        return edit_form_view(request, form)
    form.populate_obj(item)
    request.session.flash(u'Your changes have been saved.', 'success')
    return HTTPSeeOther(request.resource_url(item))
