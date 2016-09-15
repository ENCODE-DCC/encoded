'use strict';

jest.autoMockOff();


describe('DataColor Module', function() {
    var React, TestUtils, assembleGraph, graphException, context, _, collectNodes;
    var DataColors = require('../datacolors');

    describe('Returns correct colors for keys', function() {
        var testKeys = [
            'immortalized cell line',
            'tissue',
            'primary cell',
            'whole organisms',
            'stem cell',
            'in vitro differentiated cells',
            'induced pluripotent stem cell line',
            'secondary cell'
        ];
        var dataColorsInstance = new DataColors(testKeys);

        it('Returns correct colors for small array', function() {
            let testColors = dataColorsInstance.colorList(['stem cell', 'primary cell']);
            expect(testColors[0]).toEqual('#007d26');
            expect(testColors[1]).toEqual('#730173');
        });

        it('Returns medium gray for a non-existent key', function() {
            let testColors = dataColorsInstance.colorList(['stem DNA']);
            expect(testColors[0]).toEqual('#808080');
        });

        it('Wraps around the used color if more keys than colors', function() {
            let testColors = dataColorsInstance.colorList(['secondary cell']);
            expect(testColors[0]).toEqual('#fcbf3a');
        });

        it('Wraps around the used color if more keys than colors', function() {
            let testColors = dataColorsInstance.colorList(['primary cell'], {shade: 10});
            expect(testColors[0]).toEqual('#8d1b8d');
        });
    });
});
