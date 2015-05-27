// Handle browser capabilities, a la Modernizr. Can *only* be called from
// mounted components (componentDidMount method would be a good method to
// use this from), because actual DOM is needed.
module.exports.BrowserFeat = {
    feat: {},

    // Return object with browser capabilities; return from cache if available
    getBrowserCaps: function (feat) {
        if (Object.keys(this.feat).length === 0) {
            this.feat.svg = document.implementation.hasFeature('http://www.w3.org/TR/SVG11/feature#Image', '1.1');
            this.feat.canvas = (function() {
                var elem = document.createElement('canvas');
                return !!(elem.getContext && elem.getContext('2d'));
            })();
            this.feat.todataurlpng = (function() {
                var canvas = document.createElement('canvas');
                return !!(canvas && canvas.toDataURL && canvas.toDataURL('image/png').indexOf('data:image/png') === 0);
            })();

            // UA checks; should be retired as soon as possible
            this.feat.uaTrident = (function() {
                return navigator.userAgent.indexOf('Trident') > 0;
            })();
        }
        return feat ? this.feat[feat] : this.feat;
    },

    setHtmlFeatClass: function() {
        var htmlclass = [];

        this.getBrowserCaps();

        // For each set feature, add to the <html> element's class
        var keys = Object.keys(this.feat);
        var i = keys.length;
        while (i--) {
            if (this.feat[keys[i]]) {
                htmlclass.push(keys[i]);
            } else {
                htmlclass.push('no-' + keys[i]);
            }
        }

        // Now write the classes to the <html> DOM element
        document.documentElement.className = htmlclass.join(' ');
    }
};

