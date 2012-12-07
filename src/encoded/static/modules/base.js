define(['exports', 'jquery', 'underscore', 'backbone'],
function base(exports, $, _, Backbone) {

    // Underscore template settings
    // `{model.title}` for escaped text
    // `<?raw variable ?>}` for raw html interpolations
    // `<?js expression ?>` for javascript evaluations
    _.templateSettings = {
          escape : /\{(.+?)\}/g,
          interpolate : /<\?raw\s+(.+?)\?>/g,
          evaluate : /<\?js\s+(.+?)\?>/g
    };


    // Base View class implements conventions for rendering views.
    exports.View = Backbone.View.extend({
        section_id: undefined,
        title: undefined,
        description: undefined,

        // Views should define their own `template`
        template: undefined,

        // Render the view
        render: function render() {
            this.$el.html(this.template({model: this.model, view: this, '_': _}));
            return this;
        }

    });

    return exports;
});
