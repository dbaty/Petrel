from repoze.bfg.chameleon_zpt import get_template

from repoze.bfg.url import static_url
from repoze.bfg.traversal import find_root


class TemplateAPI(object):
    """Provides a master template and various information and
    utilities that can be used in any template.
    """
    def __init__(self, request):
        self.request = request
        self.referrer = request.environ.get('HTTP_REFERER', None)
        referrer = request.headers.get('Referer', '')
        if referrer.startswith(request.application_url):
            self.status_message = request.params.get('status_message', '')
            self.error_message = request.params.get('error_message', '')
        else:
            self.status_message = self.error_message = ''
        self.site = find_root(request.context)
        self.layout = get_template('templates/layout.pt')
        ## FIXME: not sure yet if this is going to be useful
        self.show_login_link = True
        if request.url.split('?')[0].endswith('login_form'):
            self.show_login_link = False
        self.user_cn = getUserMetadata(request).get('cn', None)

    ## FIXME: rename as 'url_of()'. Is it used, actually?
    def urlOf(self, path):
        ## FIXME: use repoze.bfg.url.model_url()
        return '/'.join((self.request.application_url, path)).strip('/')

    def static_url(self, path):
        return static_url(path, self.request)

    def get_nav_tree(self):
        """Return HTML code to build a navigation tree.

        This navigation tree shows:
        - all root folderish items;

        - all folderish items that are ancestors of the context;

        - all sibling items of the context.
        """
        ## FIXME: use 'get_nav_tree()' below once it is implemented.
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


## FIXME: rename as 'get_user_metadata()'
def getUserMetadata(request):
    return request.environ.get('repoze.who.identity', {})


def get_nav_tree(root): ## FIXME: to be implemented
    """Return a navigation tree from the given ``root``."""
    ## FIXME: check that our implementation needs the site to be
    ## indexed.
    return []
