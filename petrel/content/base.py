from persistent import Persistent

from pyramid.location import lineage
from pyramid.threadlocal import get_current_registry
from pyramid.url import model_url

from wtforms.fields import TextField
from wtforms.form import Form
from wtforms.validators import required

from petrel.catalog import CatalogAware
from petrel.content.registry import get_content_type_registry
from petrel.events import ObjectModifiedEvent
from petrel.views import get_default_view_bindings
from petrel.views import redirect_to


class BaseContent(Persistent, CatalogAware):

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

    def get_addable_types(self):
        return ()

    def get_url(self, request):
        return model_url(self, request).strip('/')

    def get_breadcrumbs(self):
        ## FIXME: it is slighty more complicated than this. We should
        ## return the default page of each parent in the lineage,
        ## something like:
        ## reversed([obj.getDefaultItem() for obj in lineage])
        return list(lineage(self))[::-1]


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


def content_view(request):
    return get_default_view_bindings(request)


def content_add_form(content_type, request, form=None):
    bindings = get_default_view_bindings(request)
    if form is None:
        form = content_type._get_add_form()
    ct_registry = get_content_type_registry()
    label = ct_registry[content_type.meta_type]['label']
    bindings.update(action='add%s' % content_type.meta_type,
                    load_jquery=True,
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
        ct_registry = get_content_type_registry()
        add_form_view = ct_registry[content_type.meta_type]['add_form_view']
        return add_form_view(request, form)
    item = content_type()
    form.populate_obj(item)
    context.add(form.id.data, item)
    ct_registry = get_content_type_registry()
    label = ct_registry[content_type.meta_type]['label']
    msg = (u'%s "%s" has been created and you are '
           'now viewing it.' % (label, form.title.data))
    return redirect_to(item.get_url(request), status_message=msg)


def content_edit_form(request, form=None):
    context = request.context
    content_type = context.__class__
    bindings = get_default_view_bindings(request)
    if form is None:
        form = context._get_edit_form()
    ct_registry = get_content_type_registry()
    label = ct_registry[content_type.meta_type]['label']
    bindings.update(action='edit',
                    load_jquery=True,
                    load_editor=True,
                    content_type=label,
                    add_mode=False,
                    form=form)
    return bindings


def content_edit(request):
    item = request.context
    form = item._get_edit_form(request.POST)
    if not form.validate():
        ct_registry = get_content_type_registry()
        edit_form_view = ct_registry[item.meta_type]['edit_form_view']
        return edit_form_view(request, form)
    form.populate_obj(item)
    msg = (u'Your changes have been saved.')
    return redirect_to(item.get_url(request), status_message=msg)
