/********* Table sorter script *************/
/*
 * Apply sorting controls to a table.
 * When user clicks on a th without 'nosort' class,
 * it sort table values using the td 'data-sortabledata' attribute,
 * or the td text content
 *
 */
(function($) {

function sortable(cell) {
    // convert a cell a to something sortable

	// use data-sortabledata attribute if it is defined
	var text = cell.attr('data-sortabledata');
	if (text === undefined) { text = cell.text(); }

	// A number, but not a date?
    if (text.charAt(4) !== '-' && text.charAt(7) !== '-' && !isNaN(parseFloat(text))) {
        return parseFloat(text);
    }
    return text.toLowerCase();
}

function sort(event, options) {
    var th, colnum, table, tbody, index, data, usenumbers, tsorted, $this;

    $this = $(this);
	th = $this.closest('th');
    colnum = $('th', $this.closest('tr')).index(th);
    table = $this.parents('table:first');
    tbody = table.find('tbody:first');
    tsorted = parseInt(table.attr('sorted') || '-1', 10);
    if (options && options.reverse !== undefined) {
        reverse = options.reverse;
    } else {
        reverse = tsorted === colnum;
    }

    $this.parent().find('th:not(.nosort) .sortdirection')
        .removeClass('icon-chevron-up icon-chevron-down');
    $this.children('.sortdirection')
        .removeClass('icon-chevron-up icon-chevron-down')
        .addClass(reverse ? 'icon-chevron-up' : 'icon-chevron-down');

    index = $this.parent().children('th').index(this),
    data = [],
    usenumbers = true;
    tbody.find('tr').each(function() {
        var cells, sortableitem;

        cells = $(this).children('td');
        sortableitem = sortable(cells.slice(index,index+1));
        if (isNaN(sortableitem)) { usenumbers = false; }
        data.push([
            sortableitem,
            // crude way to sort by surname and name after first choice
            sortable(cells.slice(1,2)), sortable(cells.slice(0,1)),
            this]);
    });

    if (data.length) {
        if (usenumbers) {
            data.sort(function(a,b) {return a[0]-b[0];});
        } else {
            data.sort();
        }
        if (reverse) { data.reverse(); }
        table.attr('sorted', reverse ? '' : colnum);

        // appending the tr nodes in sorted order will remove them from their old ordering
        tbody.append($.map(data, function(a) { return a[3]; }));
    }

    tbody.setoddeven();
}

// jQuery plugins
// --------------

$.fn.setoddeven = function() {
    return this.each(function() {
        // jquery :odd and :even are 0 based
        $(this).children(':not(.hidden)').removeClass('odd even')
            .filter(':odd').addClass('even').end()
            .filter(':even').addClass('odd');
    });
};

$.fn.table_sorter = function () {
    // set up blank spaceholder gif
    var blankarrow = $('<i></i>').addClass('sortdirection icon-');
    // all listing tables not explicitly nosort, all sortable th cells
    // give them a pointer cursor and blank cell and click event handler
    // the first one of the cells gets a up arrow instead.
    return this.each(function () {
        var $this = jQuery(this);
        $this.find('thead tr:not(.nosort) th:not(.nosort)')
            .append(blankarrow.clone())
            .css('cursor', 'pointer')
            .click(sort);
        $this.find('tbody').setoddeven();
        $this.find('.sort-initial:first').each(function () {
                _.bind(sort, this)(null, {reverse: $(this).hasClass('sort-initial-reverse')});
            });
    });
};

})(jQuery);
