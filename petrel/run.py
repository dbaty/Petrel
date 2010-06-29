from repoze.bfg.configuration import Configurator

from repoze.zodbconn.finder import PersistentApplicationFinder

from petrel.content.site import appmaker


def app(global_config, **settings):
    zodb_uri = settings.get('zodb_uri')
    if not zodb_uri:
        raise ValueError("No 'zodb_uri' in application configuration.")
    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    config = Configurator(root_factory=get_root, settings=settings)
    config.begin()
    config.load_zcml('configure.zcml')
    config.end()
    return config.make_wsgi_app()
