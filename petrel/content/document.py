"""Define the Document content type and everything related to it:
forms, views, etc.

$Id$
"""

from wtforms.fields import TextField
from wtforms.fields import TextAreaField
from wtforms.validators import required

from petrel.content.base import BaseContent
from petrel.content.base import BaseForm
from petrel.views import get_default_view_bindings
from petrel.views import redirect_to


class Document(BaseContent):
    def get_searchable_text(self):
        ## FIXME: we should remove HTML tags from 'body'
        return u' '.join((
                BaseContent.get_searchable_text(self), self.body))

    def get_addable_types(self):
        return ()


class DocumentEditForm(BaseForm):
    ## FIXME: check that id is not already taken
    id = TextField(label=u'Id',
                   description=u'Should be short, will be part of the URL.',
                   validators=[required()])
    title = TextField(label=u'Title', validators=[required()])
    body = TextAreaField(label=u'Body')


def document_view(request):
    return get_default_view_bindings(request)


def document_add_form(request, form=None):
    bindings = get_default_view_bindings(request)
    if form is None:
        form = DocumentEditForm()
    bindings.update(action='addDocument',
                    content_type='document',
                    add_mode=True,
                    form=form)
    return bindings


def document_add(request):
    form = DocumentEditForm(request.POST)
    if not form.validate():
        return document_add_form(request, form)

    document = Document()
    document.edit(title=form.title.data,
                  body=form.body.data)
    request.context.add(form.id.data, document)
    msg = (u'Document "%s" has been created and you are '
           'now viewing it.' % form.title.data)
    return redirect_to(document.get_url(request), status_message=msg)


def document_edit_form(request, form=None):
    bindings = get_default_view_bindings(request)
    if form is None:
        document = request.context
        form = DocumentEditForm(id=document.__name__,
                                title=document.title,
                                body=document.body)
    bindings.update(action='editDocument',
                    content_type='document',
                    add_mode=False,
                    form=form)
    return bindings 


def document_edit(request):
    form = DocumentEditForm(request.POST)
    if not form.validate():
        return document_edit_form(request, form)

    document = request.context
    document.edit(title=form.title.data,
                  body=form.body.data)
    msg = (u'Yous changes have been saved.')
    return redirect_to(document.get_url(request), status_message=msg)
