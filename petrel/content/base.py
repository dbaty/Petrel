from persistent import Persistent

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.threadlocal import get_current_registry

from petrel.search import CatalogAware
from petrel.content.registry import get_content_type_registry
from petrel.events import ObjectModifiedEvent
from petrel.views.utils import get_template_api


class BaseContent(Persistent, CatalogAware):

    is_folderish = False

    title = u''
    description = u''
    template = u'default'

    @classmethod
    def _get_add_form(cls, *args, **kwargs):
        return cls.add_form(*args, **kwargs)

    def _get_edit_form(self, request_data=None):
        if request_data is None:
            form_class = self.edit_form
            data = {}
            for field in form_class():
                # We create a fake form to get its fields. There are
                # other ways but this probably is the easiest one.
                data[field.name] = getattr(self, field.name)
            return form_class(**data)
        return self.edit_form(request_data)

    def get_searchable_text(self):
        return u' '.join((self.title, self.description))

    def edit(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if getattr(self, '__parent__', None):
            # We may be called when the item is first added. We want
            # to notify the event only if the item has already been
            # added.
            registry = get_current_registry()
            registry.notify(ObjectModifiedEvent(self))

    def get_icon(self, request):
        """Return icon and alternate text that correspond to the
        content type.
        """
        return request.static_url(self.icon), self.label

    def get_addable_types(self, request):
        return ()


def _get_display_template(ct_registry, context):
    for template_info in ct_registry[context.__class__]['display_templates']:
        if template_info['id'] == context.template:
            return template_info['template']
    return None


def content_view(request):
    ct_registry = get_content_type_registry(request.registry)
    klass = request.context.__class__
    templates = ct_registry[klass]['display_templates']
    if not templates:
        raise ValueError('The default display view is used for the %s '
                         'content type but no template has been '
                         'provided. It must be customized.' % klass.label)
    template = _get_display_template(
            ct_registry, request.context)
    api = get_template_api(request)
    return render_to_response(template,
                              {'api': api, 'context': request.context})


def content_add_form(content_type, request, form=None):
    if form is None:
        form = content_type._get_add_form()
    label = content_type.label
    return {'api': get_template_api(request),
            'load_jquery': True,
            'load_editor': True,
            'content_type': label,
            'add_mode': True,
            'form': form}


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
    context.add(request.registry, form.id.data, item)
    label = content_type.label
    msg = (u'%s "%s" has been created and you are '
           'now viewing it.' % (label, form.title.data))
    request.session.flash(msg, 'success')
    location = request.resource_url(item) + getattr(item, 'admin_view_path', '')
    return HTTPSeeOther(location)


def content_edit_form(request, form=None):
    context = request.context
    content_type = context.__class__
    if form is None:
        form = context._get_edit_form()
    label = content_type.label
    return {'api': get_template_api(request),
            'load_jquery': True,
            'load_editor': True,
            'content_type': label,
            'add_mode': False,
            'form': form}


def content_edit(request):
    item = request.context
    form = item._get_edit_form(request.POST)
    if not form.validate():
        ct_registry = get_content_type_registry(request.registry)
        ## FIXME: how can this work?
        edit_form_view = ct_registry[item]['edit_form_view']
        return edit_form_view(request, form)
    form.populate_obj(item)
    request.session.flash(u'Your changes have been saved.', 'success')
    location = request.resource_url(item) + getattr(item, 'admin_view_path', '')
    return HTTPSeeOther(location)
