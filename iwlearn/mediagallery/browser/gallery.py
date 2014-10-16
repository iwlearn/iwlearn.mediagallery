""" Controllers
"""

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.app.blob.interfaces import IBlobWrapper
from zope.component import queryMultiAdapter
import logging



class Mediagallery(BrowserView):
    """ Media gallery page
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        #gallery_properties = getattr(portal_properties,
        #                                        'gallery_properties')
        self.portal_url = getToolByName(aq_inner(context), 'portal_url')()


    def getPhotos(self):
        """ retrieves latest photos by date and by keyword """
        items = _getItems(self,
                portaltypes=('Image'),
		tags=('photo-gallery'),
                noOfItems=6)
        return items

    def getVideos(self):
        """ retrieves multimedia objects (videos/animations etc..)
        filtered by date and by topic """
        result = _getItems(self,
                portaltypes=('Link'),
		tags=('video'),
                noOfItems=6)
        return result

    def getSubjectValues(self):
        items = list(self.catalog.Indexes[
            "Subject"].uniqueValues())
        return items

def _getItems(self, portaltypes=None, tags=None,
               category=None, noOfItems=None, language=None):
    """ retrieves items of certain content types and/or interface and
    certain visibility level, with the addition of topic filtering """
    noOfItems = noOfItems or 8
    query = {
        'review_state'   : 'published',
        'sort_on'        : 'effective',
        'sort_order'     : 'reverse',
        'sort_limit'     : noOfItems
        }
    topic = getattr(self.context.REQUEST, 'topic', None)
    if portaltypes:
        query['portal_type'] = portaltypes
    if tags:
        query['Subject'] = tags
    if topic:
        query['Subject'] = [tags, topic]
    res = self.catalog(query)

    filtered_res = filterLatestVersion(self, brains=res,
                                                     noOfItems=noOfItems)
    return filtered_res

def filterLatestVersion(self, brains, noOfItems=6):
    """ Take a list of catalog brains
    and return only the first noOfItems
    which are either latest versions or not versioned.
    """
    cat = getToolByName(self.context, 'portal_catalog')
    res = []
    # NOTE: ichimdav due to the performance optimization tichet we no longer 
    # pass the catalog search with all of the results from which we can keep
    # searching for the latest version and at the end break, instead now 
    # this method receives the latest brains for the catalog search sorted
    # by effective date
    for brain in brains:
        res.append(brain)

        if len(res) == noOfItems:
            break  #we got enough items
    # because of performance optimization ticket and #14008 
    # resort based on effective date since getting the latest version could
    # mess up the sorting that came from the catalog search
    res.sort(key=lambda x: x.effective)
    res.reverse()
    return res
