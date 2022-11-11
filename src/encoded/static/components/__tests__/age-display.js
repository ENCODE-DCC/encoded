import { ageDisplayToAgeParts } from '../search';

describe('Test ageDisplayToAgeParts', () => {
    it('returns the correct object for a simple age string', () => {
        const ageParts = ageDisplayToAgeParts('1 year');
        expect(ageParts).toEqual({ age: '1', age_units: 'year' });
    });

    it('returns the correct object for a simple age string', () => {
        const ageParts = ageDisplayToAgeParts('11.5 day');
        expect(ageParts).toEqual({ age: '11.5', age_units: 'day' });
    });
});
