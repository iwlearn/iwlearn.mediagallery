jQuery(document).ready(function($) {

    $(window).bind('iwlearn.tags.loaded', function (evt, tab) {
        var $tab = $(tab);
        $tab.find('a').bind('click', function(ev){
            window.location.hash = this.id;
            ev.preventDefault();
        });
    });

    var iwlearn_tabs = function(){
        if($("#whatsnew-gallery").length) {
            return;
        }
        var $iwlearn_tabs = $(".iwlearn-tabs"), iwlearn_tabs_length = $iwlearn_tabs.length,
            $iwlearn_tabs_panels = $(".iwlearn-tabs-panels"), i = 0;
        var $iwlearn_tab, $iwlearn_tabs_panel, $iwlearn_panels, $iwlearn_tab_children;
        if (iwlearn_tabs_length) {
            for (i; i < iwlearn_tabs_length; i += 1) {
                $iwlearn_tab = $iwlearn_tabs.eq(i);
                // don't run tab logic if tab already contains tab data
                if ($iwlearn_tab.data('tabs')) {
                    $(window).trigger('iwlearn.tags.loaded', $iwlearn_tab);
                    continue;
                }
                // detach tab for dom manipulation
                $iwlearn_tab.detach();
                $iwlearn_tabs_panel = $iwlearn_tabs_panels.eq(i);

                $iwlearn_panels = $iwlearn_tabs_panel.children();
                // append iwlearn-tabs-title elements if found in iwlearn-tabs-panel
                $iwlearn_panels.find('.iwlearn-tabs-title').detach().appendTo($iwlearn_tab);

                $iwlearn_tab_children = $iwlearn_tab.children();
                var j = 0, tabs_length = $iwlearn_tab_children.length,
                    $tab_title, tab_title_text, tab_title_id;

                // the tabs need a link so we append a link if one is not found
                for (j; j < tabs_length; j += 1) {
                    $tab_title = $($iwlearn_tab_children[j]);
                    // IE 7 encloses surrounding elements withing the li so we
                    // feed it p tags and convert it to li afterwards
                    if ($tab_title[0].tagName === "P") {
                        $tab_title.replaceWith("<li>" + $tab_title.html() + "</li>");
                    }
                    if (!$tab_title.find('a').length) {
                        tab_title_text = $tab_title.text();
                        tab_title_id = tab_title_text.toLowerCase().replace(/\s/g, '-');
                        $tab_title.text("");
                        $('<a />').attr({'href' :'#tab-' + tab_title_id, 'id': 'tab-' + tab_title_id}).html(tab_title_text).appendTo($tab_title);
                    }
                }
                // redo children assignment since they could have been changed from
                // p to li
                $iwlearn_tab_children = $iwlearn_tab.children();
                $iwlearn_tab.tabs($iwlearn_panels);
                $iwlearn_tab.insertBefore($iwlearn_tabs_panel);

                $(window).trigger('iwlearn.tags.loaded', $iwlearn_tab);
            }
        }

    };
    window.IWLEARN = window.IWLEARN || {};
    // expose iwlearn_tabs function to the global window for reuse in other scripts
    window.IWLEARN.iwlearn_tabs = iwlearn_tabs;
    iwlearn_tabs();

    $(window).bind('hashchange', function (evt) {
        // #14564 trigger click only if hash contains tab and use find to avoid
        // js syntax error
        if (window.location.hash.indexOf('tab') !== -1) {
            $("#content").find(window.location.hash).click();
        }
    });

    $(window).trigger('iwlearn.tags.loaded', $('#whatsnew-gallery').find('.iwlearn-tabs'));
    $(window).trigger('iwlearn.tags.loaded', $('#multimedia-tabs'));

    if (window.location.hash) {
        $(window).trigger('hashchange');
    }

});
