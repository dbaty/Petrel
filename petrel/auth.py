"""Authorization/authentication."""

from repoze.who.config import make_api_factory_with_config

from repoze.who.plugins.zodb.users import Users

from petrel.config import SITE_ID


who_api_factory = None # will be initialized at startup


def create_user_db(site):
    setattr(site, '_users', Users())


def users_finder(root):
    site = root[SITE_ID]
    return getattr(site, '_users')


def get_who_api(environ):
    return who_api_factory(environ)


def setup_who_api_factory(global_config, conf_file, dummy=None):
    global who_api_factory
    if dummy is not None:
        who_api_factory = dummy
    else:
        who_api_factory = make_api_factory_with_config(
            global_config, conf_file)


def get_user_metadata(request):
    md = getattr(request, '__user_metadata', None)
    if md is not None:
        return md
    who_api = who_api_factory(request.environ)
    md = who_api.authenticate() or {}
    request.__user_metadata = md
    return md
