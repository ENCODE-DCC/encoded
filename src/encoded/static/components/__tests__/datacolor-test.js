import DataColors from '../datacolors';


describe('DataColor Module', () => {
    describe('Returns correct colors for keys', () => {
        const testKeys = [
            'cell line',
            'tissue',
            'primary cell',
            'whole organisms',
            'stem cell',
            'in vitro differentiated cells',
            'induced pluripotent stem cell line',
            'secondary cell',
            'organoid',
        ];
        const dataColorsInstance = new DataColors(testKeys);

        it('Returns correct colors for small array', () => {
            const testColors = dataColorsInstance.colorList(['stem cell', 'primary cell']);
            expect(testColors[0]).toEqual('#9b009b');
            expect(testColors[1]).toEqual('#FF9000');
        });

        it('Returns medium gray for a non-existent key', () => {
            const testColors = dataColorsInstance.colorList(['stem DNA']);
            expect(testColors[0]).toEqual('#808080');
        });

        it('Wraps around the used color if more keys than colors', () => {
            const testColors = dataColorsInstance.colorList(['secondary cell']);
            expect(testColors[0]).toEqual('#124E78');
        });

        it('Wraps around the used color if more keys than colors', () => {
            const testColors = dataColorsInstance.colorList(['primary cell'], { tint: 0.1 });
            expect(testColors[0]).toEqual('#ff9b19');
        });

        it('Merry-go-round if unseen key and merry-go-round in enabled', () => {
            const testColors = dataColorsInstance.colorList(['apple'], { merryGoRoundColors: true });
            expect(testColors[0]).toEqual('#2f62cf');
        });
    });
});
