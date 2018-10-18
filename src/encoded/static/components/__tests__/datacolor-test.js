import DataColors from '../datacolors';


describe('DataColor Module', () => {
    describe('Returns correct colors for keys', () => {
        const testKeys = [
            'cell line',
            'tissue',
            'primary cell',
            'whole organisms',
            'in vitro differentiated cells',
            'secondary cell',
        ];
        const dataColorsInstance = new DataColors(testKeys);

        it('Returns correct colors for small array', () => {
            const testColors = dataColorsInstance.colorList(['primary cell']);
            expect(testColors[0]).toEqual('#ff9a00');
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
