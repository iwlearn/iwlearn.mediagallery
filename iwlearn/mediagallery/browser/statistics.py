""" Statistics
"""
from Products.Five import BrowserView
from zope.component import getUtility
from iwlearn.mediagallery.interfaces import IMediaCentre

class Info(BrowserView):
    """ Info
    """

    def __init__(self, context, request):
        super(Info, self).__init__(context, request)
        self.mediacentre = getUtility(IMediaCentre)

    def getMediaStats(self):
        """ Get media stats
        """
        result = []

        types = self.mediacentre.getMediaTypes()
        for mediatype, type_info in types.items():
            data = self.mediacentre.getMedia(mediatype)
            result.append({ 'type': type_info['title'], 'count': len(data) })

        return result

    def getPluginNames(self):
        """ Get plugin names
        """
        return self.mediacentre.getPluginNames()
