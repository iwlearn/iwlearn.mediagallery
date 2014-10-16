""" Provider
"""
from zope.component import queryAdapter
from iwlearn.mediagallery.interfaces import IMediaProvider
from iwlearn.mediagallery.interfaces import IMediaDisplayInfo
from iwlearn.mediagallery.interfaces import IMediaPlayer

class MediaContainerVideos(object):
    """ Media Container Videos
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def media_items(self, media_type):
        """ Returns dicts of all media items available.
            media_type arg is a string, e.g. 'video'
        """

        provider = IMediaProvider(self.context)
        provider.media_type = media_type

        items = []
        for mfile in provider.media_items:
            mime_type = mfile.get_content_type()
            media_info = queryAdapter(mfile, IMediaDisplayInfo, mime_type)
            widget = queryAdapter(mfile, IMediaPlayer, mime_type)

            info_dict = media_info()
            if widget:
                info_dict['widget'] = widget(None, None)
            items.append(info_dict)

        return items


class MediaContainerView(object):
    """ Media Container View
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def media_items(self, media_type=None):
        """ Media items
        """
        provider = IMediaProvider(self.context)
        provider.media_type = media_type

        videos = []
        for mfile in provider.media_items:
            videos.append(mfile)

        return videos
