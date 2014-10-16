""" FLV player
"""
from zope import interface
from zope import component
from iwlearn.mediagallery.interfaces import IMediaPlayer
from Products.CMFCore import utils as cmfutils
import simplejson

class FLVVideoPlayer(object):
    """ FLV Video Player
    """
    interface.implements(IMediaPlayer)
    component.adapts(object)

    def __init__(self, context):
        self.context = context

    def __call__(self, downloadurl, imageurl, width, height):
        if downloadurl:
            try:
                contentobj = self.context.context.context
            except AttributeError:
                contentobj = self.context
        else:
            contentobj = self.context

        portal_tool = cmfutils.getToolByName(contentobj, 'portal_url')
        portal_url = portal_tool.getPortalObject().absolute_url()
        player = portal_url + "/++resource++flowplayer/flowplayer-3.2.2.swf"

        downloadurl = contentobj.absolute_url()

        # See flowplayer.org site for available options
        config = {
            'clip': {
                'url':downloadurl,
                'autoPlay': True,
                'autoBuffering': True,
                'scaling': 'fit',
                'useNativeFullScreen': True,
            },

            'canvas' : {
                    'backgroundColor' : '#000000',
                    'backgroundGradient': 'none'
            },

            'plugins': {
                'controls': {
                    'autoHide': 'never',
                    'url': portal_url + \
            '/%2B%2Bresource%2B%2Bflowplayer/flowplayer.controls-3.2.1.swf',
                    }
            },
        }
        config = simplejson.dumps(config)

        # check if aspect ratio fits in 4:3 or 16:9 and fallback to 16:9 
        # if the video aspect ratio is not 4:3 or 16:9
        aspect_ratio = ""
        if width and height:
            ratio = float(width) / float(height)
            if ratio > 1.77:
                aspect_ratio = "sixteen-nine" # 16:9
            elif ratio < 1.37: #proper is 1.33 but there are vids on production
                #which are closer to 4:3 with a ratio of 1.36 rather than 16:9
                aspect_ratio = "four-three" # 4:3
            else:
                aspect_ratio = "sixteen-nine"
        return MAIN_VIDEO_TEMPLATE % {
                                      'player': player,
                                      'title': contentobj.title,
                                      'config': config,
                                      'ratio' : aspect_ratio
                                      }

MAIN_VIDEO_TEMPLATE = """
    <div class="flowplayer">
        <div id="embeddedvideo" class="%(ratio)s">
          Please enable javascript or upgrade to
          <a href="http://www.adobe.com/go/getflashplayer">Flash Player 11</a>
          to watch the video.
        </div>

        <script type="text/javascript">
        jQuery(document).ready(function($) {
            $("#embeddedvideo").flashembed({
                src:'%(player)s',
                version: [10, 0]
              },
              {
                config:%(config)s
              }
            );
        });
        </script>

    </div>
"""
