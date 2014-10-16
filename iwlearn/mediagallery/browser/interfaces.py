""" Interfaces
"""
from zope.interface import Interface

class IPortlet(Interface):
    """ Portlet
    """

    def all_link():
        """ All link
        """
        pass

    def short_items():
        """ Short items
        """
        pass

    def full_items():
        """ Full items
        """
        pass

    def title():
        """ Title
        """
        pass

class IMediaPortlet(IPortlet):
    """ Media portlet
    """

    def all_link(self):
        """ All link
        """
        pass

    def short_items(self):
        """ Short items
        """
        pass

    def full_items(self):
        """ Full items
        """
        pass

    def items(self):
        """ Items
        """
        pass

    def media_player(self):
        """ Returns the media player for the media file.
        """

class IAutoRelated(Interface):
    """ Auto related
    """

    def autoContext():
        """ Return related items in a specific order: manually tagged,
            same region and basin, latest items.
        """

class IImageView(Interface):
    """ Returns the image stream to the requested image
    """

    def display(scalename):
        """ Says if it's OK to display an image of requested size
        """

