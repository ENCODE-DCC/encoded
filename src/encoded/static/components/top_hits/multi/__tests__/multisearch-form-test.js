import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

import NavBarForm, {
    shouldRenderResults,
    makeGroupsForResults,
} from '../form';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Forms', () => {
    test('shouldRenderResults', () => {
        expect(
            shouldRenderResults('abc', {'abc': [1, 2, 3]})
        ).toBeTruthy();
        expect(
            shouldRenderResults('abc', {'abc': []})
        ).toBeFalsy();
        expect(
            shouldRenderResults('xzy', {'abc': [3, 3]})
        ).toBeFalsy();
    });
    test('makeGroupForResults', () => {
        expect(
            makeGroupsForResults(
                'a549',
                {
                    'dataCollections': [],
                    'topHits': [{}]
                },
                () => {}
            )
        ).toHaveLength(1);
    });
    test('NavBarForm renders InputWithIcon', () => {
        const navBarForm = mount(
            <NavBarForm
                input="hello"
                handleInputChange={() => {}}
                handleClickAway={() => {}}
                results={{}}
            />
        );
        expect(
            navBarForm.find('form').props().className
        ).toEqual('multisearch__multiform');
        expect(navBarForm.find('InputWithIcon')).toHaveLength(1);
        expect(navBarForm.find('Input')).toHaveLength(1);
        expect(
            navBarForm.find('i').props().className
        ).toEqual('icon icon-search');
        expect(navBarForm.find('Results')).toHaveLength(0);
    });
});
