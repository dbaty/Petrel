from zope.interface import implements

from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.traversal import find_root

from petrel.interfaces import ITemplateAPI


def get_template_api(request):
    factory = request.registry.queryUtility(ITemplateAPI)
    return factory(request)


class TemplateAPI(object):
    """Provides various bindings usable in a template."""
    implements(ITemplateAPI)

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.site = find_root(request.context)
        ## FIXME: could be reified (?)
        self.admin_layout = get_renderer(
            'petrel:templates/admin_layout.pt').implementation()
        self.admin_toolbar = get_renderer(
            'petrel:templates/toolbar.pt').implementation().macros['toolbar']
        self.context_url = request.resource_url(request.context)

    @property
    def success_messages(self):
        return self.request.session.pop_flash('success')

    @property
    def error_messages(self):
        return self.request.session.pop_flash('error')

    def url(self, obj):
        return self.request.resource_url(obj)

    def static_url(self, path):
        return self.request.static_url(path)

    @reify ## FIXME: really?
    def logged_in(self):
        return True ## FIXME

    @property
    def toolbar_js(self): ## FIXME: rename
        if not self.logged_in:
            return ''
        css = ('<style type="text/css">'
               '#petrel-toolbar {'
               '  width: 100%;'
               '  border: 0;'
               '  z-index: 100;'
               '  position: absolute;'
               '  top: 0;'
               '  padding: 0;'
               '  margin: 0;'
               '  height: 0;'
               '}'
               '</style>')
        js = ('<script type="text/javascript">'
              'var iframe = document.createElement("iframe");'
              'iframe.id = "petrel-toolbar";'
              'iframe.src = "%s/_toolbar.html";'
              'document.body.insertBefore(iframe, document.body.firstChild);'
              '</script>' % self.request.url.strip('/'))
        return ''.join((css, js))

    def get_nav_tree(self):
        """Return HTML code to build a navigation tree.

        This navigation tree shows:

        - all root folderish items;

        - all folderish items that are ancestors of the context;

        - all sibling items of the context.
        """
        ## FIXME
        html = ''
        html += '<li><a href="#">foo</a></li>'
        html += '<li><a href="#">bar</a></li>'
        html += '<li><a href="#">baz</a>'
        html += '<ol>'
        html += '<li><a href="#">sub-baz 1</a></li>'
        html += '<li><a href="#">sub-baz 2</a></li>'
        html += '</ol></li>'
        html += '<li><a href="#">quuz</a></li>'
        html += ''
        return html

    def get_breadcrumbs(self):
        context = self.request.context
        site = find_root(context)
        site_url = self.request.resource_url(site)
        breadcrumbs = []
        while context is not site:
            breadcrumbs.append({'title': context.title,
                                'name': context.__name__})
            context = context.__parent__
        breadcrumbs.append({'title': site.title,
                            'url': site_url})
        breadcrumbs.reverse()
        url = site_url.strip('/')
        for item in breadcrumbs[1:]:
            url = item['url'] = '%s/%s' % (url, item['name'])
        return breadcrumbs

    def nav_tree(self):
        ## FIXME: check that our implementation needs the site to be
        ## indexed.
        return []
