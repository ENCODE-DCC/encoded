import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

import {
    NavBarSearch,
    PageSearch,
} from '../search';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Search', () => {
    test('NavBarSearch renders', () => {
        const search = mount(
            <NavBarSearch />
        );
        expect(search.find('NavBarForm')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(1);
    });
    test('PageSearch renders', () => {
        const search = mount(
            <PageSearch />
        );
        expect(search.find('PageForm')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(0);
    });
});
