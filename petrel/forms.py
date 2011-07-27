from wtforms.fields import TextField
from wtforms.fields import TextAreaField
from wtforms.form import Form
from wtforms.validators import required

from wtforms.widgets import TextArea


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

    def has_html_field(self):
        """Return whether the form has any HTML field."""
        for field in self:
            if isinstance(field, HtmlField):
                return True
        return False


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


class HtmlWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs['class'] = 'html'
        return TextArea.__call__(self, field, **kwargs)


class HtmlField(TextAreaField):
    widget = HtmlWidget()
