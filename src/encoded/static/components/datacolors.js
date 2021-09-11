import _ from 'underscore';


// DataColors is a class for managing symbolic data colors throughout the app. Essentially it
// statically maps data keys to colors consistently even when the data changes.
//
// Creating a new mapping of data keys to colors, passing in an array of data keys. The order of
// keys in the given array determines their color assignment.
// const biosampleTypeColors = new DataColors(biosampleTypes);
//
// With an array of data keys, return a corresponding array of colors, each one lightened by 50%:
// const colorList = biosampleTypeColors.colorList(data, {lighten: 50});


// List of colors. Those wishing to modify the colors used by this module need to modify this list.
const rootColorList = [
    '#2f62cf',
    '#de3700',
    '#FF9000',
    '#009802',
    '#9b009b',
    '#0098c8',
    '#df4076',
    '#124E78',
    '#FFC300',
    '#82ae4e',
    '#661026',
    '#2e0929',
    '#240a36',
    '#2e0e6b',
    '#9d99cd',
    '#303d4a',
    '#016879',
    '#133827',
    '#af7864',
    '#859280',
    '#6db4cf',
    '#2b07f8',
];


/**
 * Convert a CSS hex color to an object with the equivalent r, g, and b components as integers from
 * 0 to 255.
 * @param {string} color CSS hex color to convert
 * @return {object} { r, g, b } values
 */
export const colorToTriple = (color) => {
    const num = parseInt(color.slice(1), 16);
    const r = num >> 16;
    const g = (num >> 8) & 0x00FF;
    const b = num & 0x0000FF;
    return { r, g, b };
};


/**
 * Convert an object with r, g, and b components into a 6-digit, zero-filled hex color string.
 * @param {object} r, g, and b components with values from 0 to 255.
 * @return {string} Equivalent hex color string
 */
export const tripleToColor = ({ r, g, b }) => {
    const rgb = b | (g << 8) | (r << 16);
    return `#${(0x1000000 + rgb).toString(16).slice(1)}`;
};


/**
 * Convert an RGB color into the equivalent HSV color.
 * @param {object} rgbTriple { r, g, b } values from 0 to 255
 * @return {object} { h, s, v } values with h from 0 to 359, and s and v from 0 to 1
 */
export const rgbToHsv = (rgbTriple) => {
    // This calculation requires normalized R, G, and B values from 0 to 1.
    const r = rgbTriple.r / 255;
    const g = rgbTriple.g / 255;
    const b = rgbTriple.b / 255;

    // Here begins the mathematical conversion process:
    // https://www.rapidtables.com/convert/color/rgb-to-hsv.html
    const cMin = Math.min(r, g, b);
    const cMax = Math.max(r, g, b);
    let h;
    let s;
    const v = cMax;
    const delta = cMax - cMin;
    if (cMax > 0) {
        s = delta / cMax;
        if (cMax === r) {
            h = (g - b) / delta;
        } else if (cMax === g) {
            h = 2 + ((b - r) / delta);
        } else { // cMax === r
            h = 4 + ((r - g) / delta);
        }

        // Convert h from 0-1 to degrees 0-359.
        h *= 60;
        h += h < 0 ? 360 : 0;
    } else {
        // Pure black case: h, s, v all zero.
        s = 0;
        h = 0;
    }
    return { h, s, v };
};


/**
 * Convert an HSV color into the equivalent RGB color.
 * @param {object} hsvTriple { h, s, v } values with h from 0 to 359, and s and v from 0 to 1
 * @return {object} {r, g, b} color from 0 to 255
 */
export const hsvToRgb = (hsvTriple) => {
    const { s, v } = hsvTriple;
    let r;
    let g;
    let b;

    if (s > 0) {
        // This begins the H sector-based conversion process.
        // https://www.rapidtables.com/convert/color/hsv-to-rgb.html
        const h = hsvTriple.h / 60;
        const sectorH = Math.floor(h);
        const fractionH = h - sectorH;
        const p = v * (1 - s);
        const q = v * (1 - (s * fractionH));
        const t = v * (1 - (s * (1 - fractionH)));
        switch (sectorH) {
        case 0: // 0 <= H < 60 degrees
            r = v;
            g = t;
            b = p;
            break;
        case 1: // 60 <= H < 120 degrees
            r = q;
            g = v;
            b = p;
            break;
        case 2: // 120 <= H < 180 degrees
            r = p;
            g = v;
            b = t;
            break;
        case 3: // 180 <= H < 240 degrees
            r = p;
            g = q;
            b = v;
            break;
        case 4: // 240 <= H < 300 degrees
            r = t;
            g = p;
            b = v;
            break;
        default: // 300 <= H < 360 degrees
            r = v;
            g = p;
            b = q;
            break;
        }
    } else {
        // Achromatic case.
        r = v;
        g = v;
        b = v;
    }

    // Convert RGB from normalized to 0-255 integers.
    return { r: Math.round(r * 255), g: Math.round(g * 255), b: Math.round(b * 255) };
};


/**
 * Conversions from a hex RGB color to the equivalent HSV triplet often repeats with the same hex
 * color, so breaking it out lets us memoize the function. Don't need a hashing function as
 * memoize uses the hex color string as the hash by default.
 * @param {string} color Hex color to convert to an HSV triplet
 * @return {object} { h, s, v } color triplet
 */
const rColorToHsvTriple = (color) => {
    const rgbTriple = colorToTriple(color);
    return rgbToHsv(rgbTriple);
};

const colorToHsvTriple = _.memoize(rColorToHsvTriple);


/**
 * Tint a hex color by a factor from 0 to 1 to generate a new hex color. The output color tends to
 * have fewer repeated values than the input hex color, so the conversion from hsv to the output
 * hex color doesn't get memoized.
 * @param {string} color CSS color on which to apply a tint value
 * @param {number} tintFactor 0 for no change to `color`, 1 for white, and all between
 */
export const tintColor = (color, tintFactor) => {
    const hsvTriple = colorToHsvTriple(color);
    const outHsvTriple = {};
    outHsvTriple.h = hsvTriple.h;
    outHsvTriple.s = hsvTriple.s * (1 - tintFactor);
    outHsvTriple.v = hsvTriple.v + (tintFactor * (1 - hsvTriple.v));
    const rgbTriple = hsvToRgb(outHsvTriple);
    return tripleToColor(rgbTriple);
};


/**
 * Test whether a color is light or not. If it's light, then using it as a background to text makes
 * black text most readable. If it's not light, then white text would work better.
 * @param {string} color CSS hex color to test
 * @return {bool} True if `color` is a "light" color.
 */
export const isLight = (color) => {
    const { r, g, b } = colorToTriple(color);

    // YIQ equation from http://24ways.org/2010/calculating-color-contrast
    const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
    return yiq > 180;
};


class DataColors {
    constructor(keys) {
        if (keys && keys.length > 0) {
            this.keys = [...keys]; // Clone given array
        } else {
            this.keys = [];
        }
    }

    /**
     * Return an array of colors corresponding to the given array of keys.
     *
     * @param {array} keys - List to get color of
     * @param {array} options - List of changes to color output. Option are
     *      tint (Number): Percentage to lighten (positive number) or darken (negative number) each
     *          color from the root colors given at DataColors instantiation. This is a signed
     *      merryGoRoundColors (boolean): True if you want the color-output to go back to first color after reaching the end. False
     *          if you want colors to start using default color-value (#808080) after reaching the end of the list
     * @returns List of colors
     * @memberof DataColors
     */
    colorList(keys, options) {
        let colors = [];
        if (keys && keys.length > 0) {
            // Map the given keys to colors consistently
            colors = options && options.merryGoRoundColors ?
                keys.map((key, index) => {
                    const i = index % rootColorList.length;
                    const outColor = rootColorList[i % rootColorList.length];
                    return options && options.tint && options.tint > 0 ? tintColor(outColor, options.tint) : outColor;
                }) :
                keys.map((key) => {
                    let outColor;
                    const i = this.keys.indexOf(key);
                    if (i === -1) {
                        // No matching key; just return medium gray
                        outColor = '#808080';
                    } else {
                        outColor = rootColorList[i % rootColorList.length];
                    }
                    return options && options.tint && options.tint > 0 ? tintColor(outColor, options.tint) : outColor;
                });
        } else {
            // No keys provided, just provide the list of colors for the caller to use as needed,
            // optionally modified by a tint value.
            colors = (options && options.tint && options.tint !== 0) ?
                rootColorList.map((color) => tintColor(color, options.tint))
            : rootColorList;
        }
        return colors;
    }
}

// Just `import DataColors from './datacolors'` and watch the magic happen
export default DataColors;
