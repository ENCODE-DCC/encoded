// Handle browser capabilities, a la Modernizr. Can *only* be called from
// mounted components (componentDidMount method would be a good method to
// use this from), because actual DOM is needed.
module.exports.BrowserFeat = {
    feat: {},

    // Return object with browser capabilities; return from cache if available
    getBrowserCaps: function getBrowserCaps(feat) {
        if (Object.keys(this.feat).length === 0) {
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

            // Detect touch events
            this.feat.touchEnabled = (() => {
                try {
                    document.createEvent('TouchEvent');
                    return true;
                } catch (evt) {
                    return false;
                }
            })();

            // Detect hidden scroll bars
            this.feat.hiddenscroll = (() => {
                const scrollDiv = document.createElement('div');
                scrollDiv.style.width = '100px';
                scrollDiv.style.height = '1px';
                scrollDiv.style.overflow = 'scroll';
                document.body.appendChild(scrollDiv);
                const hiddenscroll = scrollDiv.offsetWidth === scrollDiv.clientWidth;
                document.body.removeChild(scrollDiv);
                return hiddenscroll;
            })();
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
