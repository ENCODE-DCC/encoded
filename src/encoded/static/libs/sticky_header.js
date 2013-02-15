(function($) {

// http://stackoverflow.com/a/6625189/199100
// http://css-tricks.com/persistent-headers/
function translate(element, x, y) {
    var translation = "translate(" + x + "px," + y + "px)";
    element.css({
        "transform": translation,
        "-ms-transform": translation,
        "-webkit-transform": translation,
        "-o-transform": translation,
        "-moz-transform": translation
    });
}

$(function() {
    $(document).scroll(function() {
        $(".sticky-header").each(function() {
            var $header = $(this),
                $table = $header.parents('.sticky-area:first'),
                offsetTop = $table.offset().top,
                scrollTop = $(window).scrollTop() + $('.navbar-fixed-top').height(),
                delta = scrollTop - offsetTop;

            if((scrollTop > offsetTop) && (scrollTop < (offsetTop + $table.height()))) {
                translate($header, 0, delta - 3); // correction for borders
            } else {
                translate($header, 0, 0);
            }
        });
    });

});

})(jQuery);
