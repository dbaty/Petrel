"""Define the Document content type and everything related to it:
forms, views, etc.

$Id$
"""

from wtforms.fields import TextAreaField

from petrel.content.base import BaseContent
from petrel.content.base import BaseContentAddForm
from petrel.content.base import BaseContentEditForm


class DocumentAddForm(BaseContentAddForm):
    body = TextAreaField(label=u'Body')


class DocumentEditForm(BaseContentEditForm, DocumentAddForm):
    pass


class Document(BaseContent):

    meta_type = 'Document'
    label = u'Document'
    icon = 'petrel:static/img/document.gif'

    add_form = DocumentAddForm
    edit_form = DocumentEditForm

    body = u''

    def get_searchable_text(self):
        ## FIXME: we should remove HTML tags from 'body'
        return u' '.join((
                BaseContent.get_searchable_text(self), self.body))
