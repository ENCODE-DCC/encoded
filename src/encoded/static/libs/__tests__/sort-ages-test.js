import sortAges from '../sort-ages';


describe('sortAges testing', () => {
    it('sorts ages with a mix of units', () => {
        const ages = [
            { age: '1', age_units: 'year' },
            { age: '2', age_units: 'week' },
            { age: '3', age_units: 'month' },
            { age: '1', age_units: 'week' },
            { age: '4', age_units: 'day' },
            { age: '5', age_units: 'year' },
            { age: '6', age_units: 'week' },
            { age: '7', age_units: 'month' },
            { age: '8', age_units: 'day' },
            { age: '9', age_units: 'year' },
        ];
        const sortedAges = sortAges(ages);
        expect(sortedAges).toEqual([
            '4 days',
            '1 week',
            '8 days',
            '2 weeks',
            '6 weeks',
            '3 months',
            '7 months',
            '1 year',
            '5 years',
            '9 years',
        ]);
    });

    it('sorts 90+ and unknown at the end and deduplicates', () => {
        const ages = [
            { age: '90 or above', age_units: 'year' },
            { age: '2', age_units: 'week' },
            { age: 'unknown' },
            { age: '1', age_units: 'week' },
            { age: '90 or above', age_units: 'year' },
            { age: '6', age_units: 'week' },
            { age: 'unknown' },
            { age: '8', age_units: 'day' },
            { age: '1', age_units: 'week' },
            { age: '9', age_units: 'year' },
        ];
        const sortedAges = sortAges(ages);
        expect(sortedAges).toEqual([
            '1 week',
            '8 days',
            '2 weeks',
            '6 weeks',
            '9 years',
            '90 or above years',
            'unknown',
        ]);
    });

    it('doesnt dedup when specifically requested not to', () => {
        const ages = [
            { age: '90 or above', age_units: 'year' },
            { age: '2', age_units: 'week' },
            { age: 'unknown' },
            { age: '1', age_units: 'week' },
            { age: '90 or above', age_units: 'year' },
            { age: '6', age_units: 'week' },
            { age: 'unknown' },
            { age: '8', age_units: 'day' },
            { age: '1', age_units: 'week' },
            { age: '9', age_units: 'year' },
        ];
        const sortedAges = sortAges(ages, { dedupe: false });
        expect(sortedAges).toEqual([
            '1 week',
            '1 week',
            '8 days',
            '2 weeks',
            '6 weeks',
            '9 years',
            '90 or above years',
            '90 or above years',
            'unknown',
            'unknown',
        ]);
    });
});
