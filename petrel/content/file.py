from wtforms.fields import FileField

from ZODB.blob import Blob

from petrel.content.base import BaseContent
from petrel.forms import BaseContentAddForm
from petrel.forms import BaseContentEditForm

## FIXME: add missing mime types
ICONS = {'application/pdf': ('PDF', 'mime_pdf.png'),
         'application/msword': ('Microsoft Word', 'mime_word.png'),
         'application/excel': ('Microsoft Excel', 'mime_excel.png'),
         }


class FileAddForm(BaseContentAddForm):
    file = FileField(label=u'File')

    def populate_obj(self, obj):
        data = self.data
        data.pop('id', None)
        data.pop('file')
        obj.edit(**data)
        field = self.file.data
        mimetype = field.headers.get('Content-Type', 'application/octet-stream')
        obj.upload(mimetype, field.filename, field.file)


# FIXME: we need a better edit form that proposes to keep the current
# file instead of forcing to re-upload it.
class FileEditForm(BaseContentEditForm, FileAddForm):
    pass


class File(BaseContent):

    meta_type = 'File'
    label = 'File'
    icon = 'petrel:static/img/type_file.png'
    file = '' # FIXME: temporary while we fix the edit form

    add_form = FileAddForm
    edit_form = FileEditForm

    def __init__(self):
        BaseContent.__init__(self)
        self.blob = Blob()

    def upload(self, mimetype, filename, stream):
        self.mimetype = mimetype
        self.filename = filename
        f = self.blob.open('w')
        size = upload_stream(stream, f)
        f.close()
        self.size = size

    def get_icon(self, request):
        """Return icon and alernate text that correspond to the MIME
        type of the file.
        """
        label, icon = ICONS.get(self.mimetype, ('Unknown', 'mime_unknown.png'))
        icon = request.static_url('petrel:static/img/%s' % icon)
        return icon, label


def upload_stream(stream, file):
    size = 0
    while 1:
        data = stream.read(1<<21)
        if not data:
            break
        size += len(data)
        file.write(data)
    return size
