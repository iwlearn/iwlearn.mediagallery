""" Video
"""
from Products.Archetypes.interfaces import ISchema
from Products.CMFCore.utils import getToolByName
from iwlearn.mediagallery.interfaces import IVideo, IMediaPlayer
from zope.component import queryAdapter
from zope.component import adapts
from zope.interface import Interface, implements
from zope import schema

from zope.schema import ValidationError
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser import BrowserView

import re

KEY = 'iwlearn.mediagallery.multimedia'


def fancy_time_amount(v, show_legend=True):
    """Produce a friendly representation of the given time amount.  The
    value is expected to be in seconds as an int.

      >>> fancy_time_amount(391)
      u'06:31 (mm:ss)'

      >>> fancy_time_amount(360)
      u'06:00 (mm:ss)'

      >>> fancy_time_amount(6360)
      u'01:46:00 (hh:mm:ss)'

      >>> fancy_time_amount(360, False)
      u'06:00'

    """

    remainder = v
    hours = remainder / 60 / 60
    remainder -= hours * 60 * 60
    mins = remainder / 60
    secs = remainder - (mins * 60)

    if hours > 0:
        val = u'%02i:%02i:%02i' % (hours, mins, secs)
        legend = u' (hh:mm:ss)'
    else:
        val = u'%02i:%02i' % (mins, secs)
        legend = u' (mm:ss)'

    if show_legend:
        full = val + legend
    else:
        full = val

    return full


def getPublishedDate(obj):
    """ Get Published Date
    """
    time = obj.EffectiveDate()
    tool = getToolByName(obj, 'translation_service')
    return tool.ulocalized_time(time, None, None, obj,
                                domain='plone')


def cloudUrl(obj):
    """ Retrieve cloudUrl field information
    """
    cloud_url = False
    mapping = IAnnotations(obj.context)
    multimedia = mapping.get('iwlearn.mediagallery.multimedia')
    if multimedia:
        cloud_url = multimedia.get('cloud_url')
    return cloud_url


#class InvalidCloudUrl(ValidationError, Exception):
#    "Please enter a video link from Youtube or Vimeo only"
#    pass


def validateCloudUrl(value):
    """ formlib validator for the cloudUrl field
    """
    if value:
        if ('youtu' not in value and 'vimeo' not in value):
            raise InvalidCloudUrl(value)
    return True


class IVideoView(Interface):
    """ Video view
    """

    def media_types(self):
        """ Media types
        """
        pass

    def duration(self):
        """ Duration
        """
        pass

    def author(self):
        """ Author
        """
        pass

    def published_date(self):
        """ Published date
        """
        pass

    def width_incl_player(self):
        """ Width incl player
        """
        pass


class VideoView(BrowserView):
    """ Video view
    """

    def __init__(self, context, request):

        super(VideoView, self).__init__(context, request)
        self.context = context
        self.request = request


    def duration(self):
        """ duration
        """
        time = self.video.get('duration')
        if time:
            time = int(round(time or 0.0))
            return fancy_time_amount(time, show_legend=False)
        else:
            return None

    def author(self):
        """ Author
        """
        return self.video.get('video_author')

    def published_date(self):
        """ Published date
        """
        return getPublishedDate(self.context)

    def width_incl_player(self):
        """ Width  incl player
        """
        return self.video.get('width', 600) + 35

    def rich_description(self):
        """ Width  incl player
        """
        return self.context.getField('text').get(self.context)

    def cloud_url(self, uid):
        """ Cloud Url
        """
        r_catalog = getToolByName(self.context, "reference_catalog")
        return r_catalog.lookupObject(uid).getRemoteUrl()


    def media_player(self):
        """ Returns the flowplayer embed string
        """
        media_player = queryAdapter(self.context,
                                    interface=IMediaPlayer,
                                    name=u"video/x-flv")
        width = self.video.get('width', 600)
        height = self.video.get('height', 380)

        if media_player is None:
            return None
            # downloadUrl and ImageUrl are the params that we send as None since
        # they are  not needed
        s = u'<div class="media-player">%s</div>' % media_player(None, None,
                                                                 width, height)
        return s

    def video_cloud_validator(self, cloud_value):
        """ check if cloudUrl has a youtube or vimeo link, saves the id
        in an annotation and save a clean link to the video for the field
        """

        value = cloud_value

        if value:
            youtube_id = re.compile(r'[0-9a-zA-z\-_]{8,}[A-Z]*')
            youtube_url = "http://www.youtube.com/watch?v="
            vimeo_url = "http://vimeo.com/"
            

            if ('youtu' and 'playlist' in value):
                # transform youtube playlist link 
                res = youtube_id.findall(value)[1]
                vid_id = 'videoseries&' + 'list=' + res
                value = 'http://www.youtube.com/playlist?list=' + res
                values =[]
                values.append(value)
                values.append("youtube")

            elif ('youtu' in value):
                # check youtube links with youtu since they might be
                # used with youtu.be our youtube.com links
                res = youtube_id.findall(value)
                if 'list' in value:
                    vid_id = res[0] + '?list=' + res[1]
                else:
                    vid_id = res[0]
                #value = youtube_url + vid_id
                value = vid_id
                values =[]
                values.append(value)
                values.append("youtube")

            elif ('vimeo' in value):
                vimeo = re.compile(r'[\d]{5,}')
                vid_id = vimeo.findall(value)[0]
                value = vimeo_url + vid_id
                values =[]
                values.append(value)
                values.append("vimeo")
            else:
                return "Please enter a video link from Youtube or Vimeo only"
        return values


class CloudVideoView(BrowserView):
    """ CloudVideo BrowserView
    """

    def cloud_url(self):
        """ Retrieve cloudUrl entry
        """
        return cloudUrl(self)

    def author(self):
        """ Author info
        """
        pass

    def rich_description(self):
        """ Rich Description
        """
        return self.context.getField('text').get(self.context)


class VideoUtils(object):
    """ A browser view for video utility methods.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def showEditMetadataTab(self):
        """ Show Edit Metadata Tab
        """
        mship = getToolByName(self.context, 'portal_membership')
        if mship.isAnonymousUser():
            return False

        if not self.context.isTranslatable():
            return False

        current = self.context.getLanguage()
        return current != 'en'
