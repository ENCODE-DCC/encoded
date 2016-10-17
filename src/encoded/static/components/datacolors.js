'use strict';
// DataColors is a class for managing symbolic data colors throughout the app. Essentially it
// statically maps data keys to colors consistently even when the data changes. 
//
// Creating a new mapping of data keys to colors, passing in an array of data keys. The order of
// keys in the given array determines their color assignment.
// var biosampleTypeColors = new DataColors(biosampleTypes);
//
// With an array of data keys, return a corresponding array of colors, each one lightened by 50%:
// var colorList = biosampleTypeColors.colorList(data, {lighten: 50});


// List of colors. Those wishing to modify the colors used by this module need to modify this list.
const rootColorList = [
    '#2f62cf',
    '#de3700',
    '#ff9a00',
    '#009802',
    '#9b009b',
    '#0098c8',
    '#df4076'
];


class DataColors {
    constructor(keys) {
        this.keys = [...keys]; // Clone given array
    }

    // Darken or lighten the given hex color by the given percentage (integer).
    // http://stackoverflow.com/questions/5560248/programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors
    shadeColor(color, percent) {
        let num = parseInt(color.slice(1), 16);
        let amt = Math.round(2.55 * percent);
        let R = (num >> 16) + amt;
        let G = (num >> 8 & 0x00FF) + amt;
        let B = (num & 0x0000FF) + amt;

        return (
            '#' + (0x1000000 + (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
                    (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
                    (B < 255 ? (B < 1 ? 0 : B) : 255))
                    .toString(16).slice(1)
        );
    }

    // Return an array of colors corresponding to the given array of keys.
    // You can pass optional options in the `options` object.
    //
    // options:
    //     shade (Number): Percentage to lighten (positive number) or darken (negative number) each
    //         color from the root colors given at DataColors instantiation. This is a signed
    //         integer -- do not pass a string with a "%" sign at the end.
    colorList(keys, options) {
        var colors = keys.map(key => {
            let outColor;
            let i = this.keys.indexOf(key);
            if (i === -1) {
                // No matching key; just return medium gray
                outColor = '#808080';
            } else {
                outColor = rootColorList[i % rootColorList.length];
            }
            return options && options.shade && options.shade !== 0 ? this.shadeColor(outColor, options.shade) : outColor;
        });
        return colors;
    }
}

// Just `require('DataColors') and watch the magic happen
module.exports = DataColors;
