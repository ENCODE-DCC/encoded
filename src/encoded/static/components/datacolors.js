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
    '#fcbf3a',
    '#1a207b',
    '#730173',
    '#7c7b82',
    '#007d26',
    '#f46036',
    '#d7263d'
];


class DataColors {
    constructor(keys) {
        this.keys = [...keys]; // Clone given array
    }

    colorList(keys, options) {
        var colors = keys.map(key => {
            let i = this.keys.indexOf(key);
            if (i === -1) {
                // No matching key; just return white
                return '#ffffff';
            }
            return rootColorList[i % rootColorList.length];
        });
        return colors;
    }
}


module.exports = DataColors;
