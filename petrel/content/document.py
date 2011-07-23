from wtforms.fields import TextAreaField

from petrel.content.base import BaseContent
from petrel.forms import BaseContentAddForm
from petrel.forms import BaseContentEditForm


class DocumentAddForm(BaseContentAddForm):
    body = TextAreaField(label=u'Body')


class DocumentEditForm(BaseContentEditForm, DocumentAddForm):
    pass


class Document(BaseContent):

    meta_type = 'Document'
    label = u'Document'
    icon = 'petrel:static/img/type_document.png'

    add_form = DocumentAddForm
    edit_form = DocumentEditForm

    body = u''

    def get_searchable_text(self):
        ## FIXME: we should remove HTML tags from 'body', remove stop
        ## words, etc.
        return u' '.join((
                BaseContent.get_searchable_text(self), self.body))
