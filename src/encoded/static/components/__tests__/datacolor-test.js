import DataColors from '../datacolors';


describe('DataColor Module', () => {
    describe('Returns correct colors for keys', () => {
        const testKeys = [
            'immortalized cell line',
            'tissue',
            'primary cell',
            'whole organisms',
            'stem cell',
            'in vitro differentiated cells',
            'induced pluripotent stem cell line',
            'secondary cell',
        ];
        const dataColorsInstance = new DataColors(testKeys);

        it('Returns correct colors for small array', () => {
            const testColors = dataColorsInstance.colorList(['stem cell', 'primary cell']);
            expect(testColors[0]).toEqual('#9b009b');
            expect(testColors[1]).toEqual('#ff9a00');
        });

        it('Returns medium gray for a non-existent key', () => {
            const testColors = dataColorsInstance.colorList(['stem DNA']);
            expect(testColors[0]).toEqual('#808080');
        });

        it('Wraps around the used color if more keys than colors', () => {
            const testColors = dataColorsInstance.colorList(['secondary cell']);
            expect(testColors[0]).toEqual('#2f62cf');
        });

        it('Wraps around the used color if more keys than colors', () => {
            const testColors = dataColorsInstance.colorList(['primary cell'], { shade: 10 });
            expect(testColors[0]).toEqual('#ffb41a');
        });
    });
});
