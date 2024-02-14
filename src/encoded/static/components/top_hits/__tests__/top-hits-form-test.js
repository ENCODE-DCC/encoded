import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

import {
    NavBarForm,
    PageForm,
} from '../form';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Forms', () => {
    test('NavBarForm renders InputWithIcon', () => {
        const navBarForm = mount(
            <NavBarForm
                input="hello"
                handleInputChange={() => {}}
                handleClickAway={() => {}}
                results={[]}
            />
        );
        expect(
            navBarForm.find('form').props().className
        ).toEqual('top-hits-search__form');
        expect(navBarForm.find('InputWithIcon')).toHaveLength(1);
        expect(navBarForm.find('Input')).toHaveLength(1);
        expect(
            navBarForm.find('i').props().className
        ).toEqual('icon icon-search');
        expect(navBarForm.find('Results')).toHaveLength(0);
    });
    test('PageForm does not render InputWithIcon', () => {
        const pageForm = mount(
            <PageForm
                input="hello"
                handleInputChange={() => {}}
                handleClickAway={() => {}}
                results={[]}
            />
        );
        expect(
            pageForm.find('form').props().className
        ).toEqual('top-hits-search__form');
        expect(pageForm.find('InputWithIcon')).toHaveLength(0);
        expect(pageForm.find('Input')).toHaveLength(1);
        expect(pageForm.find('Results')).toHaveLength(0);
    });
});
