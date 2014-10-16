/*global jQuery window*/
jQuery(document).ready(function($) {
    'use strict';
    var ie = $.browser.msie  && parseInt($.browser.version, 10);

    // 13830 add last-child class since ie < 9 doesn't know about this css3 selector
    $("#whatsnew-gallery").find('.iwlearn-tabs').find('li:last-child').addClass('last-child');

});
