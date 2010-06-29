from zope.interface import implements

from petrel.interfaces import IObjectModifiedEvent


class ObjectModifiedEvent(object):
    implements(IObjectModifiedEvent)

    def __init__(self, object):
        self.object = object
