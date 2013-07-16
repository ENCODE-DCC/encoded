define(['exports', 'registry'],
function (globals, Registry) {
    /*jshint devel: true*/
    'use strict';

    // Item pages
    globals.content_views = Registry();

    // Panel detail views
    globals.panel_views = Registry();

    // Cell name listing titles
    globals.listing_titles = Registry();


    globals.itemClass = function (context, htmlClass) {
        htmlClass = htmlClass || '';
        (context['@type'] || []).forEach(function (type) {
            htmlClass += ' type-' + type;
        });
        if (typeof context.status == 'string') {
            htmlClass += ' status-' + context.status.toLowerCase();
        }
        return htmlClass;
    };

    return globals;
});
