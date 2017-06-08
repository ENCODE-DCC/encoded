// Handle browser capabilities, a la Modernizr. Can *only* be called from
// mounted components (componentDidMount method would be a good method to
// use this from), because actual DOM is needed.
module.exports.BrowserFeat = {
    feat: {},

    // Return object with browser capabilities; return from cache if available
    getBrowserCaps: function getBrowserCaps(feat) {
        if (Object.keys(this.feat).length === 0) {
            // Detect SVG
            this.feat.svg = document.implementation.hasFeature('http://www.w3.org/TR/SVG11/feature#Image', '1.1');

            // Detect <canvas>
            this.feat.canvas = (() => {
                const elem = document.createElement('canvas');
                return !!(elem.getContext && elem.getContext('2d'));
            })();

            // Detect toDataURL
            this.feat.todataurlpng = (() => {
                const canvas = document.createElement('canvas');
                return !!(canvas && canvas.toDataURL && canvas.toDataURL('image/png').indexOf('data:image/png') === 0);
            })();

            // Detect CSS transforms
            this.feat.csstransforms = (() => {
                const elem = document.createElement('tspan');
                return 'transform' in elem.style;
            })();

            // Detect FlexBox
            this.feat.flexbox = (() => {
                const elem = document.createElement('tspan');
                return 'flexBasis' in elem.style;
            })();

            // UA checks; should be retired as soon as possible
            this.feat.uaEdge = (() => navigator.userAgent.indexOf('Edge') > 0)();

            // UA checks; should be retired as soon as possible
            this.feat.uaTrident = (() => navigator.userAgent.indexOf('Trident') > 0)();
        }
        return feat ? this.feat[feat] : this.feat;
    },

    setHtmlFeatClass: function setHtmlFeatClass() {
        const htmlclass = [];

        this.getBrowserCaps();

        // For each set feature, add to the <html> element's class
        const keys = Object.keys(this.feat);
        keys.forEach((key) => {
            if (this.feat[key]) {
                htmlclass.push(key);
            } else {
                htmlclass.push(`no-${key}`);
            }
        });

        // Now write the classes to the <html> DOM element
        document.documentElement.className = htmlclass.join(' ');
    },
};
