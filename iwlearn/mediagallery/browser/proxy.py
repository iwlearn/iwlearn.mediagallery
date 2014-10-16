""" Proxy
"""
from Products.CMFPlone import utils
from zope.component import getMultiAdapter, getUtility
from zope.interface import alsoProvides
from iwlearn.mediagallery.interfaces import IMediaCentre

class MediaTypeProxy(utils.BrowserView):
    """ Media Type Proxy
    """

    def video_items(self, media_type):
        """ Video items
        """
        mediacentre = getUtility(IMediaCentre)
        types = mediacentre.getMediaTypes()
        iface = types[media_type]['provider']

        alsoProvides(self, iface)
        view = getMultiAdapter((self, self.request), name="video_provider")

        return view.video_items()
