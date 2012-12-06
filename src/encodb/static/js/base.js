define(['exports', 'jquery', 'underscore', 'backbone'],
function base(exports, $, _, Backbone) {

    // Base View class implements conventions for rendering views.
    exports.View = Backbone.View.extend({

        // Views should define `template`

        // Render the view
        render: function render() {
            this.$el.html(this.template);
            return this;
        }

    });

    return exports;
});
