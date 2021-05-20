import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

import NavBarMultiSearch from '../search';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('NavBarMultiSearch', () => {
    test('NavBarMultiSearch renders', () => {
        const search = mount(
            <NavBarMultiSearch />
        );
        expect(search.find('NavBarForm')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(1);
    });
});
