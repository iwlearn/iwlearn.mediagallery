// Integration JS between fancybox and IWLearn
jQuery(document).ready(function($) {
    $('.pop a').prepOverlay(
        {
            subtype: 'image',
            urlmatch: '/image_.+$',
            urlreplace: ''
        }
    );
});

