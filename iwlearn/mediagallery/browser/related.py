""" Related
"""
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from iwlearn.mediagallery.interfaces import IMediaType
from iwlearn.mediagallery.browser.interfaces import IAutoRelated
from Products.ATContentTypes.interfaces.link import IATLink as MIVideo
from iwlearn.mediagallery.interfaces import IMediaPlayer
from zope.schema.interfaces import IVocabularyFactory
from zope.component import (
    queryAdapter, getUtility,
    getMultiAdapter, queryMultiAdapter
)
from zope.interface import implements

import logging

logger = logging.getLogger('iwlearn.mediagallery.browser.related')

TOP_VIDEOS = 3
MEDIA_ORDER = ['video']

def getObjectInfo(item, request):
    """ Object info
    """
    plone_utils = getToolByName(item, 'plone_utils')
    wf_tool = getToolByName(item, 'portal_workflow')
    state = getMultiAdapter((item, request), name="plone_context_state")

    item_type_class = plone_utils.normalizeString(item.portal_type)
    item_wf_state = wf_tool.getInfoFor(item, 'review_state', '')
    item_wf_state_class = 'state-' + plone_utils.normalizeString(item_wf_state)
    url = state.view_url()
    mimetype = item.get_content_type()
    imgview = item.thumbnail
    info = { 'title': item.Title,
             'uid': item.UID,
             'description': item.Description,
             'url': item.getURL(),
             'has_img': imgview != None,
             'item_thumbnail':item.thumbnail,
             'item_type': item.portal_type,
             'item_mimetype':mimetype,
             'item_type_class': item_type_class,
             'item_wf_state': item_wf_state,
             'item_wf_state_class': item_wf_state_class }

    return info

def getOrigObjectInfo(item):
    """ Object info
    """
    plone_utils = getToolByName(item, 'plone_utils')
    wf_tool = getToolByName(item, 'portal_workflow')
    item_type_class = plone_utils.normalizeString(item.portal_type)
    item_wf_state = wf_tool.getInfoFor(item, 'review_state', '')
    mimetype = item.get_content_type()
    info = { 'title': item.Title(),
             'uid': item.UID(),
             'description': item.Description(),
             'url': item._getURL(),
             'item_type': item.portal_type,
             'item_mimetype':mimetype,
             'item_type_class': item_type_class }

    return info


def filterDuplicates(items):
    """ filter duplicates by overriding uid keys with latest dict value
    """

    uids = OrderedDict()
    for i in items:
        uids[i['uid']] = i
    return uids.values()


def others(context, request, brains):
    """Returns a list of brains which do no point to the context
    """
    plone_utils = getToolByName(context, 'plone_utils')
    cid = context.getId()
    if context.portal_type == "Image":
        return (getObjectInfo(b, request) for b in brains if (b.getId != cid))
    elif context.portal_type == "Link":
        return (getObjectInfo(b, request) for b in brains if ((b.getId != cid) and ('youtu' in b.getObject().remoteUrl or 'vimeo' in b.getObject().remoteUrl)))


class AutoRelated(object):
    """ Auto related
    """
    implements(IAutoRelated)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def autoContext(self, portal_type=None, fill_limit=None, item_id=None, show_orig=False):
        """NOTE: returns full info. May end up being slow
           Remove "video" and "photo-gallery" keyword from subject tags
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        fill_limit = fill_limit or 25
        defaultConstraints = {'review_state': 'published',
                              'sort_limit': fill_limit}

        query = defaultConstraints
        query['portal_type'] = portal_type

        item_subject = tuple(x for x in self.context.Subject() if (x != "video" and x!="photo-gallery"))

        try:
            parent_path = '/'.join(self.context.getParentNode().getPhysicalPath())
            p_query = dict(query)
            p_query['path'] = parent_path
            parent_result = catalog(p_query)
        except AttributeError:
            parent_path=''
        if len(item_subject) > 0:
            s_query = dict(query)
            s_query['Subject'] = item_subject
            subject_result = catalog(s_query)
        try:
            item_basin = self.context.getBasin()
            b_query = dict(query)
            b_query['getBasin'] = item_basin
            basin_result = catalog(b_query) 
        except AttributeError:
            item_basin=''
        try:
            item_region = self.context.getSubRegions()
            r_query = dict(query)
            r_query['getSubRegions'] = item_region
            region_result = catalog(r_query) 
        except AttributeError:
            item_region=''
        
        if parent_path:
            results = parent_result
        if len(item_subject) > 0:
            results += subject_result
        if item_basin:
            results += basin_result     
        if item_region:
            results += region_result
        
        items = others(self.context, self.request, results)
        nondups = filterDuplicates(items)
        if show_orig:
            orig = getOrigObjectInfo(self.context)
            return [orig] + nondups
        else:
            return nondups


