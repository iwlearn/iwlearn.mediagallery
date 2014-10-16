""" File image
"""

import logging
from Products.Five.browser import BrowserView
logger = logging.getLogger('eea.mediacentre')

class ViewImage(BrowserView):
    """ A view for streaming image content. This overrides the
        p4a.fileimage.browser.ViewImage view because of flowplayer.
        image urls must end with .jpg or .png, otherwise flowplayer
        doesn't figure out what type of image it is, so we add the
        extension to the url and remove it here.
    """

    def __call__(self):
        field = self.request.form.get('field', '::').split(':')
        if len(field) < 3:
            logger.warning("Could not get proper fieldname for request %s"
                           " with query string %s",
                           self.request.URL, self.request.get('QUERY_STRING'))
            return ""

        ifpackagename, ifname, fieldname = field
        if not fieldname:
            logger.warning("Could not get proper fieldname for request %s"
                           " with query string %s",
                           self.request.URL, self.request.get('QUERY_STRING'))
            return ""

        if fieldname.endswith('.jpg') or fieldname.endswith('.png'):
            fieldname = fieldname[:-4]
        try:
            ifpackage = __import__(ifpackagename, {}, {}, ifpackagename)
            iface = getattr(ifpackage, ifname)
            adapted = iface(self.context)
            value = getattr(adapted, fieldname, '')
        except Exception:
            value = self.context.getField('image')
            if value:
                accessor = value.getAccessor(self.context)()
                if accessor:
                    return accessor.index_html(self.request,
                                               self.request.response)
                else:
                    value = ""
        if not value:
            logger.warn("Could not get proper fieldname for request %s"
                        " with query string %s",
                        self.request.URL, self.request.get('QUERY_STRING'))
            return ""

        return value.index_html(self.request, self.request.response)
