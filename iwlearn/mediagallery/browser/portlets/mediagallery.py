""" Media Gallery portlet
"""
from StringIO import StringIO
from time import localtime

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets import cache
from plone.app.portlets.portlets import base

PLMF = MessageFactory('plonelocales')

class IMediagalleryPortlet(IPortletDataProvider):
    """A portlet displaying a media gallery (pictures and videos).
    """
    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=6)

    photo_location = schema.TextLine(title=_(u'Photo Locations'),
                       description=_(u'Indicate what folders should be searched for images.'),
                       required=True,
                       default=_(u'events;iw-projects'))

    video_keyword = schema.TextLine(title=_(u'Video keywords'),
                       description=_(u'Keywords to search for videos.'),
                       required=True,
                       default=_(u'Video'))


class Assignment(base.Assignment):
    implements(IMediagalleryPortlet)

    photo_location = None
    video_keyword = None

    def __init__(self, count=6, photo_location=None, video_keyword=None):
        self.count = count
        self.photo_location = photo_location
        self.video_keyword = video_keyword

    @property
    def title(self):
        return _(u"Mediagallery")

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        self.data = data

    render = ViewPageTemplateFile('mediagallery.pt')


    def getResults(self, portal_type=None):
        """ retrieves latest photos filtererd by location, videos by keyword """
        if portal_type == "Image":
            items = _getItems(self,
                    portaltypes=portal_type,
		            location=self.data.photo_location,
                    noOfItems=self.data.count)
        else:
            items = _getItems(self,
                    portaltypes=portal_type,
		            tags=self.data.video_keyword,
                    noOfItems=self.data.count)
        
        return items

    def getSubjectValues(self):
        items = list(self.catalog.Indexes[
            "Subject"].uniqueValues())
        return items

def _reindexItems(self, portaltypes='Link', tags='video',
               category=None, noOfItems=None, language=None):
    """ reindexes current link items - DELETE AFTER USE """
    noOfItems = noOfItems or 8
    query = {
        'review_state'   : 'published',
        'sort_on'        : 'effective',
        'sort_order'     : 'reverse'
        }
    topic = getattr(self.context.REQUEST, 'topic', None)
    if portaltypes:
        query['portal_type'] = portaltypes
    if tags:
        query['Subject'] = tags
    res = self.catalog(query)
    for item in res:
        item.getObject().reindexObject()

def _getItems(self, portaltypes=None, location=None, tags=None,
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
    if location:
        site = getSite()
        location_values = location.split(";")
        location_list = []
        for location in location_values:
            location_list.append('/'.join(site.getPhysicalPath()) + "/" + location)
        query['path'] = location_list
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


class AddForm(base.AddForm):
    form_fields = form.Fields(IMediagalleryPortlet)
    label = _(u"Add Media gallery Portlet")
    description = _(u"This portlet displays a media gallery.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IMediagalleryPortlet)
    label = _(u"Edit Media gallery Portlet")
    description = _(u"This portlet displays a media gallery")
