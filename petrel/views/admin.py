from petrel.views.utils import get_template_api

def toolbar(request):
    return {'api': get_template_api(request),
            }
