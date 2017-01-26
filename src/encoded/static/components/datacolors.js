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
    '#df4076',
];


class DataColors {
    constructor(keys) {
        if (keys && keys.length) {
            this.keys = [...keys]; // Clone given array
        } else {
            this.keys = [];
        }
    }

    // Darken or lighten the given hex color by the given percentage (integer).
    // http://stackoverflow.com/questions/5560248/programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors
    static shadeColor(color, percent) {
        const num = parseInt(color.slice(1), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = ((num >> 8) & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;

        return (
            `#${(0x1000000 + ((R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000) +
                    ((G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100) +
                    (B < 255 ? (B < 1 ? 0 : B) : 255))
                    .toString(16).slice(1)}`
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
        let colors = [];
        if (keys && keys.length) {
            // Map the given keys to colors consistently
            colors = keys.map((key) => {
                let outColor;
                const i = this.keys.indexOf(key);
                if (i === -1) {
                    // No matching key; just return medium gray
                    outColor = '#808080';
                } else {
                    outColor = rootColorList[i % rootColorList.length];
                }
                return options && options.shade && options.shade !== 0 ? DataColors.shadeColor(outColor, options.shade) : outColor;
            });
        } else {
            // No keys provided, just provide the list of colors for the caller to use as needed,
            // optionally modified by a shade value.
            colors = (options && options.shade && options.shade !== 0) ?
                rootColorList.map(color => DataColors.shadeColor(color, options.shade))
            : rootColorList;
        }
        return colors;
    }
}

// Just `import DataColors from './datacolors'` and watch the magic happen
export default DataColors;
